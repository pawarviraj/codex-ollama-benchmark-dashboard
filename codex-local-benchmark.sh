#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="profile"
PROFILE="local_ollama_auto"
MODEL="gpt-oss:20b"
OUTPUT_DIR=""
SITE_DIR="${ROOT_DIR}/docs"
SITE_CONFIG="${ROOT_DIR}/site-config.json"
TIMEOUT_SECS="180"
KEEP_WORKSPACES="0"
DOC_URL="https://developers.openai.com/codex/noninteractive"

usage() {
  cat <<'EOF'
Usage:
  ./codex-local-benchmark.sh [options]

Options:
  --mode profile|native-oss   Runner mode. Default: profile
  --profile NAME              Codex profile to use in profile mode. Default: local_ollama_auto
  --model TAG                 Ollama model to use in native-oss mode. Default: gpt-oss:20b
  --output-dir DIR            Where to write traces and reports. Default: /tmp/codex-benchmark-<timestamp>
  --site-dir DIR              Where to publish the static benchmark dashboard. Default: ./docs
  --site-config FILE          Optional site metadata config for GitHub Pages/SEO. Default: ./site-config.json
  --timeout SECONDS           Per-test timeout. Default: 180
  --keep-workspaces           Keep generated test workspaces in the report directory
  --help                      Show this help

Examples:
  ./codex-local-benchmark.sh
  ./codex-local-benchmark.sh --mode native-oss --model gpt-oss:120b
  ./codex-local-benchmark.sh --mode profile --profile local_ollama_auto
  ./codex-local-benchmark.sh --site-dir /path/to/dashboard
  ./codex-local-benchmark.sh --site-config /path/to/site-config.json
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="${2:-}"
      shift 2
      ;;
    --profile)
      PROFILE="${2:-}"
      shift 2
      ;;
    --model)
      MODEL="${2:-}"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="${2:-}"
      shift 2
      ;;
    --site-dir)
      SITE_DIR="${2:-}"
      shift 2
      ;;
    --site-config)
      SITE_CONFIG="${2:-}"
      shift 2
      ;;
    --timeout)
      TIMEOUT_SECS="${2:-}"
      shift 2
      ;;
    --keep-workspaces)
      KEEP_WORKSPACES="1"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$MODE" in
  profile|native-oss)
    ;;
  *)
    echo "Unsupported mode: $MODE" >&2
    exit 2
    ;;
esac

timestamp="$(date +%Y%m%d-%H%M%S)"
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/codex-benchmark-${timestamp}}"
TRACE_DIR="${OUTPUT_DIR}/traces"
WORKSPACE_DIR="${OUTPUT_DIR}/workspaces"
SUMMARY_MD="${OUTPUT_DIR}/summary.md"
SUMMARY_TSV="${OUTPUT_DIR}/summary.tsv"
SUMMARY_JSON="${OUTPUT_DIR}/summary.json"

mkdir -p "$TRACE_DIR" "$WORKSPACE_DIR"

if command -v timeout >/dev/null 2>&1; then
  TIMEOUT_CMD=(timeout --signal=TERM --kill-after=10 "${TIMEOUT_SECS}")
else
  TIMEOUT_CMD=()
fi

log() {
  printf '%s\n' "$*" >&2
}

run_codex_json() {
  local workdir="$1"
  local prompt="$2"
  local trace="$3"

  if [[ "$MODE" == "profile" ]]; then
    "${TIMEOUT_CMD[@]}" \
      codex exec \
      --ephemeral \
      --profile "$PROFILE" \
      --json \
      --skip-git-repo-check \
      -C "$workdir" \
      "$prompt" >"$trace" 2>&1
  else
    "${TIMEOUT_CMD[@]}" \
      codex exec \
      --ephemeral \
      --oss \
      --local-provider ollama \
      -m "$MODEL" \
      --full-auto \
      --json \
      --skip-git-repo-check \
      -C "$workdir" \
      -c 'web_search="live"' \
      "$prompt" >"$trace" 2>&1
  fi
}

run_codex_json_capture() {
  local workdir="$1"
  local prompt="$2"
  local trace="$3"
  local rc=0

  set +e
  run_codex_json "$workdir" "$prompt" "$trace"
  rc=$?
  set -e

  printf '%s' "$rc"
}

extract_last_agent_message() {
  python3 - "$1" <<'PY'
import json
import sys

last = ""
with open(sys.argv[1], "r", encoding="utf-8", errors="ignore") as fh:
    for line in fh:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("type") == "item.completed":
            item = obj.get("item", {})
            if item.get("type") == "agent_message":
                last = item.get("text", "")
print(last)
PY
}

count_command_executions() {
  python3 - "$1" <<'PY'
import json
import sys

count = 0
with open(sys.argv[1], "r", encoding="utf-8", errors="ignore") as fh:
    for line in fh:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("type") == "item.completed":
            item = obj.get("item", {})
            if item.get("type") == "command_execution":
                count += 1
print(count)
PY
}

detect_dedicated_web_search() {
  python3 - "$1" <<'PY'
import json
import sys

found = False
with open(sys.argv[1], "r", encoding="utf-8", errors="ignore") as fh:
    for line in fh:
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        item = obj.get("item", {}) if obj.get("type") in {"item.started", "item.completed"} else {}
        item_type = str(item.get("type", "")).lower()
        for candidate in (
            item_type,
            str(item.get("name", "")).lower(),
            str(item.get("tool", "")).lower(),
            str(obj.get("name", "")).lower(),
            str(obj.get("tool", "")).lower(),
        ):
            if "web_search" in candidate or ("search" in candidate and candidate not in {"reasoning", "command_execution"}):
                found = True
                break
        if found:
            break
print("yes" if found else "no")
PY
}

trace_uses_shell_http() {
  local trace="$1"
  if rg -q 'curl .*developers\.openai\.com/codex/noninteractive|wget .*developers\.openai\.com/codex/noninteractive|python3? -c .*developers\.openai\.com/codex/noninteractive' "$trace"; then
    echo "yes"
  else
    echo "no"
  fi
}

fetch_ground_truth_title() {
  curl -fsSL "$DOC_URL" | python3 -c 'import re, sys; html=sys.stdin.read(); m=re.search(r"<title>(.*?)</title>", html, re.I|re.S); print(m.group(1).strip() if m else "")'
}

record_result() {
  local test_name="$1"
  local status="$2"
  local details="$3"
  local trace="$4"

  printf '%s\t%s\t%s\t%s\n' "$test_name" "$status" "$details" "$trace" >>"$SUMMARY_TSV"
  printf '| %s | %s | %s | `%s` |\n' "$test_name" "$status" "$details" "$trace" >>"$SUMMARY_MD"
}

setup_edit_test_workspace() {
  local dir="$1"
  mkdir -p "$dir"
  printf 'status=pending\n' >"${dir}/config.txt"
  printf '%s\n' '#!/usr/bin/env bash' 'set -euo pipefail' "grep -qx 'status=done' ${dir}/config.txt" >"${dir}/test.sh"
  chmod +x "${dir}/test.sh"
}

run_create_file_test() {
  local name="create_file"
  local dir="${WORKSPACE_DIR}/${name}"
  local trace="${TRACE_DIR}/${name}.jsonl"
  local prompt="Create a file named notes.txt containing exactly READY, then answer exactly CREATED and stop."
  local rc=0

  mkdir -p "$dir"
  rc="$(run_codex_json_capture "$dir" "$prompt" "$trace")"

  local answer
  answer="$(extract_last_agent_message "$trace")"
  local commands
  commands="$(count_command_executions "$trace")"
  local status="FAIL"
  local details="rc=${rc}; answer=${answer}; command_exec=${commands}"

  if [[ $rc -eq 0 ]] && [[ -f "${dir}/notes.txt" ]] && [[ "$(cat "${dir}/notes.txt")" == "READY" ]] && [[ "$answer" == "CREATED" ]]; then
    status="PASS"
  elif [[ $rc -eq 124 ]]; then
    status="TIMEOUT"
  fi

  record_result "$name" "$status" "$details" "$trace"
}

run_edit_and_test() {
  local name="edit_and_test"
  local dir="${WORKSPACE_DIR}/${name}"
  local trace="${TRACE_DIR}/${name}.jsonl"
  local prompt="Read config.txt, change the status from pending to done, run ./test.sh, and answer exactly PASS if the test succeeds, then stop."
  local rc=0

  setup_edit_test_workspace "$dir"
  rc="$(run_codex_json_capture "$dir" "$prompt" "$trace")"

  local answer
  answer="$(extract_last_agent_message "$trace")"
  local commands
  commands="$(count_command_executions "$trace")"
  local status="FAIL"
  local details="rc=${rc}; answer=${answer}; command_exec=${commands}"

  if [[ $rc -eq 0 ]] && [[ "$(cat "${dir}/config.txt")" == "status=done" ]] && bash "${dir}/test.sh" >/dev/null 2>&1 && [[ "$answer" == "PASS" ]]; then
    status="PASS"
  elif [[ $rc -eq 124 ]]; then
    status="TIMEOUT"
  fi

  record_result "$name" "$status" "$details" "$trace"
}

run_shell_http_test() {
  local name="shell_http"
  local dir="${WORKSPACE_DIR}/${name}"
  local trace="${TRACE_DIR}/${name}.jsonl"
  local prompt="Using shell commands, fetch the exact HTML <title> text of ${DOC_URL} and answer with only that exact title text, then stop."
  local rc=0
  local expected
  expected="$(fetch_ground_truth_title)"

  mkdir -p "$dir"
  rc="$(run_codex_json_capture "$dir" "$prompt" "$trace")"

  local answer
  answer="$(extract_last_agent_message "$trace")"
  local commands
  commands="$(count_command_executions "$trace")"
  local shell_http
  shell_http="$(trace_uses_shell_http "$trace")"
  local status="FAIL"
  local details="rc=${rc}; answer=${answer}; expected=${expected}; command_exec=${commands}; shell_http=${shell_http}"

  if [[ $rc -eq 0 ]] && [[ "$answer" == "$expected" ]] && [[ "$commands" -ge 1 ]]; then
    status="PASS"
  elif [[ $rc -eq 124 ]]; then
    status="TIMEOUT"
  fi

  record_result "$name" "$status" "$details" "$trace"
}

run_web_search_test() {
  local name="web_search_tool"
  local dir="${WORKSPACE_DIR}/${name}"
  local trace="${TRACE_DIR}/${name}.jsonl"
  local prompt="Use Codex web search, not shell commands or direct HTTP requests, to find the exact HTML <title> text of ${DOC_URL}. Answer with only that exact title text, then stop."
  local rc=0
  local expected
  expected="$(fetch_ground_truth_title)"

  mkdir -p "$dir"
  rc="$(run_codex_json_capture "$dir" "$prompt" "$trace")"

  local answer
  answer="$(extract_last_agent_message "$trace")"
  local dedicated
  dedicated="$(detect_dedicated_web_search "$trace")"
  local shell_http
  shell_http="$(trace_uses_shell_http "$trace")"
  local status="FAIL"
  local details="rc=${rc}; answer=${answer}; expected=${expected}; dedicated_web_search=${dedicated}; shell_http=${shell_http}"

  if [[ $rc -eq 0 ]] && [[ "$answer" == "$expected" ]] && [[ "$dedicated" == "yes" ]]; then
    status="PASS"
  elif [[ $rc -eq 0 ]] && [[ "$answer" == "$expected" ]] && [[ "$shell_http" == "yes" ]]; then
    status="PARTIAL"
  elif [[ $rc -eq 0 ]] && [[ "$answer" == "$expected" ]]; then
    status="PARTIAL"
  elif [[ $rc -eq 124 ]]; then
    status="TIMEOUT"
  fi

  record_result "$name" "$status" "$details" "$trace"
}

write_summary_header() {
  cat >"$SUMMARY_MD" <<EOF
# Codex Local Benchmark

- Timestamp: ${timestamp}
- Mode: ${MODE}
- Profile: ${PROFILE}
- Model: ${MODEL}
- Output directory: ${OUTPUT_DIR}
- Ground truth URL: ${DOC_URL}

| Test | Status | Details | Trace |
| --- | --- | --- | --- |
EOF

  printf 'test\tstatus\tdetails\ttrace\n' >"$SUMMARY_TSV"
}

cleanup_workspaces() {
  if [[ "$KEEP_WORKSPACES" != "1" ]]; then
    rm -rf "$WORKSPACE_DIR"
  fi
}

write_summary_json() {
  python3 - "$SUMMARY_TSV" "$SUMMARY_JSON" "$timestamp" "$MODE" "$PROFILE" "$MODEL" "$OUTPUT_DIR" "$DOC_URL" <<'PY'
import json
import os
import sys

summary_tsv, summary_json, timestamp, mode, profile, model, output_dir, doc_url = sys.argv[1:]
tests = []
with open(summary_tsv, "r", encoding="utf-8") as fh:
    next(fh, None)
    for line in fh:
        line = line.rstrip("\n")
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) != 4:
            continue
        test, status, details, trace = parts
        tests.append(
            {
                "test": test,
                "status": status,
                "details": details,
                "trace": trace,
            }
        )

counts = {"PASS": 0, "PARTIAL": 0, "FAIL": 0, "TIMEOUT": 0}
for item in tests:
    counts[item["status"]] = counts.get(item["status"], 0) + 1

score_map = {"PASS": 1.0, "PARTIAL": 0.5, "FAIL": 0.0, "TIMEOUT": 0.0}
score = 0.0
if tests:
    score = sum(score_map.get(item["status"], 0.0) for item in tests) / len(tests)

payload = {
    "timestamp": timestamp,
    "mode": mode,
    "profile": profile,
    "model": model,
    "output_dir": output_dir,
    "doc_url": doc_url,
    "tests": tests,
    "counts": counts,
    "score": round(score, 3),
}

with open(summary_json, "w", encoding="utf-8") as fh:
    json.dump(payload, fh, indent=2)
    fh.write("\n")
PY
}

publish_dashboard() {
  python3 "${ROOT_DIR}/generate_benchmark_site.py" \
    --run-dir "$OUTPUT_DIR" \
    --site-dir "$SITE_DIR" \
    --timestamp "$timestamp" \
    --mode "$MODE" \
    --profile "$PROFILE" \
    --model "$MODEL" \
    --doc-url "$DOC_URL" \
    --site-config "$SITE_CONFIG"
}

log "Writing benchmark output to ${OUTPUT_DIR}"
write_summary_header
run_create_file_test
run_edit_and_test
run_shell_http_test
run_web_search_test
cleanup_workspaces

pass_count="$(awk -F '\t' 'NR > 1 && $2 == "PASS" {c++} END {print c+0}' "$SUMMARY_TSV")"
partial_count="$(awk -F '\t' 'NR > 1 && $2 == "PARTIAL" {c++} END {print c+0}' "$SUMMARY_TSV")"
fail_count="$(awk -F '\t' 'NR > 1 && ($2 == "FAIL" || $2 == "TIMEOUT") {c++} END {print c+0}' "$SUMMARY_TSV")"

{
  echo
  echo "Summary:"
  echo "- PASS: ${pass_count}"
  echo "- PARTIAL: ${partial_count}"
  echo "- FAIL/TIMEOUT: ${fail_count}"
} | tee -a "$SUMMARY_MD"

write_summary_json
publish_dashboard

printf '\nBenchmark complete.\nSummary: %s\nDashboard: %s/index.html\n' "$SUMMARY_MD" "$SITE_DIR"
