# Ollama Codex Benchmark

This repository publishes a public benchmark site for testing how well local Ollama models work with Codex for real development tasks.

The benchmark measures:

- file creation
- file editing
- terminal command execution
- test execution
- shell-based web access
- dedicated Codex web-search behavior

The site is generated automatically after each benchmark run and is designed to be committed to GitHub and served from GitHub Pages using the `docs/` folder.

## Quick Start

Run the benchmark:

```bash
cd /home/pawarviraj/automated_development/codex-benchmark-dashboard
./codex-local-benchmark.sh --mode native-oss --model gpt-oss:20b
```

This updates:

- `docs/index.html`
- `docs/runs/<run-id>/`
- `docs/site-data.json`
- `docs/robots.txt`
- `docs/sitemap.xml`

