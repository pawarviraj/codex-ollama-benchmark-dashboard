# Codex Local Benchmark

- Timestamp: 20260324-202749
- Mode: native-oss
- Profile: local_ollama_auto
- Model: gpt-oss:20b
- Output directory: /tmp/codex-benchmark-20260324-202749
- Ground truth URL: https://developers.openai.com/codex/noninteractive

| Test | Status | Details | Trace |
| --- | --- | --- | --- |
| create_file | PASS | rc=0; answer=CREATED; command_exec=1 | `/tmp/codex-benchmark-20260324-202749/traces/create_file.jsonl` |
| edit_and_test | PASS | rc=0; answer=PASS; command_exec=4 | `/tmp/codex-benchmark-20260324-202749/traces/edit_and_test.jsonl` |
| shell_http | PASS | rc=0; answer=Non-interactive mode – Codex | OpenAI Developers; expected=Non-interactive mode – Codex | OpenAI Developers; command_exec=2; shell_http=yes | `/tmp/codex-benchmark-20260324-202749/traces/shell_http.jsonl` |
| web_search_tool | TIMEOUT | rc=124; answer=; expected=Non-interactive mode – Codex | OpenAI Developers; dedicated_web_search=no; shell_http=yes | `/tmp/codex-benchmark-20260324-202749/traces/web_search_tool.jsonl` |

Summary:
- PASS: 3
- PARTIAL: 0
- FAIL/TIMEOUT: 1
