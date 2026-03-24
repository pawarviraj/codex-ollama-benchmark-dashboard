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

## GitHub Pages Setup

1. Update [site-config.json](/home/pawarviraj/automated_development/codex-benchmark-dashboard/site-config.json) with your real GitHub username and repository name.
2. Initialize the repository if needed:

```bash
cd /home/pawarviraj/automated_development/codex-benchmark-dashboard
git add .
git commit -m "Publish Ollama Codex benchmark site"
```

3. Create a GitHub repository and push it:

```bash
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME.git
git push -u origin main
```

4. In GitHub, enable Pages from the `main` branch and the `/docs` folder.

## Search Visibility

This project includes the practical SEO pieces that help search engines understand the site:

- strong page titles and descriptions
- canonical URLs when `site_url` is configured
- structured data
- `robots.txt`
- `sitemap.xml`
- stable per-run pages
- crawlable static HTML

That improves discoverability for queries like `ollama codex benchmark`, but no implementation can honestly guarantee a top ranking. Search position depends on indexing, competition, backlinks, freshness, and domain authority.

## Notes

- Do not set your local-only DNS name `ollama.homelab-server.work` as the GitHub Pages site URL unless you also own and publish that domain publicly.
- The public site should use a public GitHub Pages URL or a real public custom domain.
- The local benchmark and local DNS setup can still stay exactly as they are on your machine.
