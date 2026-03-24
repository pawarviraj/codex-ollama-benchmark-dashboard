# Local Codex Benchmark

This benchmark checks the parts of Codex that matter most for local development with Ollama:

- file creation
- file editing
- command execution
- test execution
- shell-based internet access
- dedicated Codex web-search behavior

It is not an exhaustive test of every Codex feature, but it is a good compatibility check for local dev workflows.

## Files

- Script: `/home/pawarviraj/automated_development/codex-benchmark-dashboard/codex-local-benchmark.sh`
- Site generator: `/home/pawarviraj/automated_development/codex-benchmark-dashboard/generate_benchmark_site.py`
- Site config: `/home/pawarviraj/automated_development/codex-benchmark-dashboard/site-config.json`
- Per-run reports: written to `/tmp/codex-benchmark-<timestamp>/` by default
- Static dashboard: `/home/pawarviraj/automated_development/codex-benchmark-dashboard/docs/index.html`

## Requirements

- Ollama running locally
- Codex CLI installed
- A local model pulled into Ollama
- Internet access if you want the shell/network and web-search checks to run

If you use the existing local profile I set up earlier, this is enough:

```bash
codex-local
codex-local-exec
```

For the official Ollama route, Codex and Ollama both document:

```bash
codex --oss
codex --oss -m gpt-oss:120b
```

Sources:
- https://docs.ollama.com/integrations/codex
- https://ollama.com/blog/codex

## Quick Start

Run against your current profile setup:

```bash
cd /home/pawarviraj/automated_development/codex-benchmark-dashboard
./codex-local-benchmark.sh
```

Every run automatically republishes the dashboard at:

```bash
/home/pawarviraj/automated_development/codex-benchmark-dashboard/docs/index.html
```

Run against the native Codex + Ollama integration path:

```bash
cd /home/pawarviraj/automated_development/codex-benchmark-dashboard
./codex-local-benchmark.sh --mode native-oss --model gpt-oss:20b
```

Try a stronger local model:

```bash
cd /home/pawarviraj/automated_development/codex-benchmark-dashboard
./codex-local-benchmark.sh --mode native-oss --model gpt-oss:120b
```

Keep the generated test workspaces for inspection:

```bash
./codex-local-benchmark.sh --keep-workspaces
```

Publish the dashboard somewhere else:

```bash
./codex-local-benchmark.sh --site-dir /path/to/benchmark-site
```

Use a different public-site metadata file:

```bash
./codex-local-benchmark.sh --site-config /path/to/site-config.json
```

Open the dashboard locally:

```bash
xdg-open /home/pawarviraj/automated_development/codex-benchmark-dashboard/docs/index.html
```

If you want to serve it over your LAN instead of opening the file directly:

```bash
cd /home/pawarviraj/automated_development/codex-benchmark-dashboard/docs
python3 -m http.server 8090
```

## How To Read Results

The benchmark writes:

- `summary.md`: human-readable report
- `summary.tsv`: easy to parse in scripts
- `summary.json`: structured metadata for the dashboard publisher
- `traces/*.jsonl`: raw Codex execution traces
- `docs/index.html`: the aggregated webpage
- `docs/runs/<run-id>/`: one archived page and artifact set per run
- `docs/robots.txt`, `docs/sitemap.xml`, and `docs/.nojekyll`: public-site publishing metadata

Status meanings:

- `PASS`: the model used the required behavior and produced the correct result
- `PARTIAL`: the result was correct, but the model used a fallback path
- `FAIL`: the result was wrong or the required file/test state was not produced
- `TIMEOUT`: the model did not complete within the configured time

The most important distinction is in `web_search_tool`:

- `PASS` means the trace suggests a dedicated search tool was used and the answer was correct
- `PARTIAL` usually means the model bypassed dedicated web search and used shell networking such as `curl`
- `FAIL` means it guessed or produced the wrong answer

## Web Dashboard

The dashboard is rebuilt automatically every time you run the benchmark.

What gets updated:

- the homepage with all historical runs
- the latest result for each model
- one detail page per run
- archived `summary.*` files and raw traces for that run
- GitHub Pages-friendly metadata such as `robots.txt`, `sitemap.xml`, and structured page metadata

This means you can benchmark models one after another and keep a persistent local comparison site without any manual export step.

## Publishing Publicly

The benchmark now defaults to publishing into `docs/`, which is the easiest GitHub Pages layout for a repository-backed static site.

Before pushing publicly:

1. Update `/home/pawarviraj/automated_development/codex-benchmark-dashboard/site-config.json` with your real GitHub username and repository name.
2. Keep using your local DNS name `ollama.homelab-server.work` only for your LAN setup, not as the public Pages URL unless that domain is actually public and delegated to GitHub Pages.
3. Commit the repository and enable GitHub Pages from the `docs/` folder on your default branch.

This setup helps the site get indexed for searches like `ollama codex benchmark`, but no site generator can honestly guarantee a top result in search rankings.

## Recommended Local Models For Codex

From current official sources:

- `gpt-oss:20b` is the default model Codex uses with Ollama
- `gpt-oss:120b` is the stronger open-weight model and should be the best local fit for Codex quality if your machine can handle it

Why:

- Ollama’s Codex integration docs say Codex defaults to local `gpt-oss:20b` and explicitly support switching to `gpt-oss:120b`
- OpenAI’s model docs describe `gpt-oss-120b` as the most powerful open-weight model
- Ollama’s model library offers both tags directly

Source highlights:

- Ollama Codex docs recommend at least a 64k context window:
  https://docs.ollama.com/integrations/codex
- Ollama blog says Codex works with `gpt-oss:20b` and `gpt-oss:120b`, defaulting to `gpt-oss:20b`:
  https://ollama.com/blog/codex
- Ollama library lists both tags:
  https://ollama.com/library/gpt-oss
- OpenAI model docs describe `gpt-oss-120b` as the most powerful open-weight model:
  https://developers.openai.com/api/docs/models/gpt-oss-120b
- OpenAI model docs describe `gpt-oss-20b` as the lower-latency local/specialized option:
  https://developers.openai.com/api/docs/models/gpt-oss-20b

Note:

- Ollama’s January 15, 2026 blog post mentions at least 32k tokens.
- The current Codex integration page says at least 64k tokens.
- I recommend following the current integration page and setting 64k or higher.

## What I Recommend For Your Machine

Given your 96 GB Ryzen AI Max+ system, the best model to try first for maximum Codex compatibility is:

```bash
ollama run gpt-oss:120b
```

Then benchmark it with:

```bash
./codex-local-benchmark.sh --mode native-oss --model gpt-oss:120b
```

If latency is too high or the system starts paging too hard, fall back to:

```bash
ollama run gpt-oss:20b
./codex-local-benchmark.sh --mode native-oss --model gpt-oss:20b
```

This recommendation is an inference from the official sources above plus the local tests we already ran: `gpt-oss:120b` should be the most compatible local Ollama-downloadable option, while `gpt-oss:20b` remains the practical lower-latency fallback.
