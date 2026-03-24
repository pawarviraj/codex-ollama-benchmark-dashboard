#!/usr/bin/env python3
import argparse
import html
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


CSS = """
:root {
  --bg: #f4efe4;
  --panel: #fffaf0;
  --panel-strong: #f6ead0;
  --ink: #1f1b16;
  --muted: #675d4f;
  --line: #d7c6a3;
  --accent: #0d7c66;
  --accent-2: #b85c38;
  --pass: #177245;
  --partial: #936f17;
  --fail: #a63c2e;
  --timeout: #7d3b74;
  --shadow: 0 18px 45px rgba(34, 27, 20, 0.08);
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  font-family: "IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif;
  color: var(--ink);
  background:
    radial-gradient(circle at top right, rgba(184, 92, 56, 0.12), transparent 28%),
    radial-gradient(circle at top left, rgba(13, 124, 102, 0.10), transparent 24%),
    linear-gradient(180deg, #f8f3e8 0%, var(--bg) 100%);
}

a {
  color: var(--accent);
}

.shell {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 28px 0 48px;
}

.hero {
  background:
    linear-gradient(145deg, rgba(255, 250, 240, 0.96), rgba(246, 234, 208, 0.95)),
    linear-gradient(120deg, rgba(13, 124, 102, 0.1), rgba(184, 92, 56, 0.08));
  border: 1px solid rgba(215, 198, 163, 0.95);
  border-radius: 28px;
  padding: 28px;
  box-shadow: var(--shadow);
}

.eyebrow {
  margin: 0 0 10px;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: var(--accent-2);
}

h1, h2, h3 {
  margin: 0;
  font-family: "Space Grotesk", "Trebuchet MS", sans-serif;
  font-weight: 700;
}

h1 {
  font-size: clamp(2rem, 5vw, 3.6rem);
  line-height: 0.98;
  max-width: 14ch;
}

h2 {
  font-size: clamp(1.35rem, 2.2vw, 1.8rem);
}

.subhead {
  margin: 14px 0 0;
  max-width: 66ch;
  color: var(--muted);
  font-size: 1rem;
  line-height: 1.6;
}

.meta-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 12px;
  border-radius: 999px;
  background: rgba(255, 250, 240, 0.9);
  border: 1px solid rgba(215, 198, 163, 0.95);
  color: var(--muted);
  font-size: 0.92rem;
}

.grid {
  display: grid;
  gap: 18px;
  margin-top: 22px;
}

.stats {
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
}

.detail-grid {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
}

.info-grid {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.panel {
  background: rgba(255, 250, 240, 0.92);
  border: 1px solid rgba(215, 198, 163, 0.95);
  border-radius: 22px;
  padding: 18px;
  box-shadow: var(--shadow);
}

.panel strong {
  color: var(--ink);
}

.stat-label {
  font-size: 0.82rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}

.stat-value {
  margin-top: 10px;
  font-family: "Space Grotesk", "Trebuchet MS", sans-serif;
  font-size: 2rem;
}

.section {
  margin-top: 24px;
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.section-copy {
  color: var(--muted);
  font-size: 0.95rem;
  line-height: 1.5;
}

.list {
  margin: 12px 0 0;
  padding-left: 18px;
  color: var(--muted);
  line-height: 1.6;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 13px 12px;
  border-bottom: 1px solid rgba(215, 198, 163, 0.75);
  vertical-align: top;
  text-align: left;
}

th {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}

tbody tr:hover {
  background: rgba(246, 234, 208, 0.4);
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 76px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 700;
  color: white;
}

.badge-PASS { background: var(--pass); }
.badge-PARTIAL { background: var(--partial); }
.badge-FAIL { background: var(--fail); }
.badge-TIMEOUT { background: var(--timeout); }

.mono {
  font-family: "IBM Plex Mono", "Fira Code", monospace;
  font-size: 0.92rem;
}

.kv {
  margin-top: 8px;
  color: var(--muted);
  line-height: 1.5;
}

.hero-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 18px;
  color: var(--ink);
  text-decoration: none;
  font-weight: 600;
}

.hero-link:hover {
  text-decoration: underline;
}

.footer-note {
  margin-top: 26px;
  color: var(--muted);
  font-size: 0.9rem;
  line-height: 1.6;
}

.lede {
  font-size: 1.04rem;
  color: var(--muted);
  line-height: 1.65;
}

code {
  font-family: "IBM Plex Mono", "Fira Code", monospace;
  background: rgba(246, 234, 208, 0.72);
  padding: 1px 5px;
  border-radius: 6px;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

@media (max-width: 760px) {
  .shell {
    width: min(100% - 20px, 1180px);
  }

  .hero,
  .panel {
    border-radius: 18px;
  }

  th:nth-child(4),
  td:nth-child(4) {
    display: none;
  }
}
"""


DEFAULT_SITE_CONFIG = {
    "site_name": "Ollama Codex Benchmark",
    "site_tagline": "Automated local-model compatibility reports for Codex and Ollama",
    "site_description": (
        "Public benchmark reports comparing how well local Ollama models work with "
        "Codex for file creation, editing, terminal execution, test runs, shell HTTP, "
        "and Codex web-search behavior."
    ),
    "site_url": "",
    "repo_url": "",
    "owner_name": "Pawar Viraj",
    "owner_github": "",
    "keywords": [
        "ollama codex benchmark",
        "codex ollama benchmark",
        "local llm coding benchmark",
        "gpt-oss benchmark",
        "ollama coding benchmark",
        "codex local development benchmark",
        "ollama codex github pages",
    ],
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--site-dir", required=True)
    parser.add_argument("--timestamp", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--doc-url", required=True)
    parser.add_argument("--site-config")
    return parser.parse_args()


def slugify(value: str) -> str:
    value = value.lower().replace(":", "-").replace("/", "-")
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "run"


def parse_timestamp(raw: str) -> datetime:
    return datetime.strptime(raw, "%Y%m%d-%H%M%S")


def pretty_timestamp(raw: str) -> str:
    return parse_timestamp(raw).strftime("%b %d, %Y at %H:%M:%S")


def iso_timestamp(raw: str) -> str:
    return parse_timestamp(raw).replace(tzinfo=timezone.utc).isoformat()


def load_summary(summary_json: Path) -> dict:
    return json.loads(summary_json.read_text(encoding="utf-8"))


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_run_files(run_dir: Path, archive_dir: Path) -> None:
    for name in ("summary.md", "summary.tsv", "summary.json"):
        src = run_dir / name
        if src.exists():
            shutil.copy2(src, archive_dir / name)

    traces_src = run_dir / "traces"
    traces_dst = archive_dir / "traces"
    if traces_dst.exists():
        shutil.rmtree(traces_dst)
    if traces_src.exists():
        shutil.copytree(traces_src, traces_dst)


def resolve_run_id(site_dir: Path, timestamp: str, mode: str, model: str, source_run_dir: str) -> str:
    runs_dir = site_dir / "runs"
    ensure_dir(runs_dir)
    base = f"{timestamp}-{slugify(mode)}-{slugify(model)}"
    candidate = base
    counter = 2

    while True:
        current = runs_dir / candidate / "run.json"
        if not current.exists():
            return candidate
        try:
            payload = json.loads(current.read_text(encoding="utf-8"))
        except Exception:
            return candidate
        if payload.get("source_run_dir") == source_run_dir:
            return candidate
        candidate = f"{base}-{counter}"
        counter += 1


def merge_site_config(raw: dict) -> dict:
    config = dict(DEFAULT_SITE_CONFIG)
    config.update(raw or {})
    config["site_url"] = sanitize_public_url(str(config.get("site_url", "")).strip())
    config["repo_url"] = sanitize_public_url(str(config.get("repo_url", "")).strip())
    owner_github = str(config.get("owner_github", "")).strip()
    if owner_github.startswith("YOUR_"):
        owner_github = ""
    config["owner_github"] = owner_github
    config["owner_name"] = str(config.get("owner_name", DEFAULT_SITE_CONFIG["owner_name"])).strip()
    config["site_name"] = str(config.get("site_name", DEFAULT_SITE_CONFIG["site_name"])).strip()
    config["site_tagline"] = str(config.get("site_tagline", DEFAULT_SITE_CONFIG["site_tagline"])).strip()
    config["site_description"] = str(config.get("site_description", DEFAULT_SITE_CONFIG["site_description"])).strip()
    keywords = config.get("keywords", DEFAULT_SITE_CONFIG["keywords"])
    if not isinstance(keywords, list):
        keywords = DEFAULT_SITE_CONFIG["keywords"]
    config["keywords"] = [str(item).strip() for item in keywords if str(item).strip()]
    return config


def load_site_config(path: str | None) -> dict:
    if not path:
        return merge_site_config({})
    config_path = Path(path)
    if not config_path.exists():
        return merge_site_config({})
    return merge_site_config(json.loads(config_path.read_text(encoding="utf-8")))


def sanitize_public_url(value: str) -> str:
    if not value:
        return ""
    if "YOUR_" in value or "<" in value or ">" in value:
        return ""
    if not re.match(r"^https?://", value):
        return ""
    return value.rstrip("/")


def xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def absolute_url(site: dict, relative_path: str) -> str:
    if not site.get("site_url"):
        return ""
    return f"{site['site_url']}/{relative_path.lstrip('/')}"


def build_run_payload(args, run_dir: Path, archive_dir: Path, summary: dict, run_id: str) -> dict:
    counts = summary.get("counts", {})
    tests = summary.get("tests", [])
    total = len(tests)
    score = summary.get("score", 0.0)

    payload = {
        "run_id": run_id,
        "timestamp": args.timestamp,
        "timestamp_pretty": pretty_timestamp(args.timestamp),
        "timestamp_iso": iso_timestamp(args.timestamp),
        "mode": args.mode,
        "profile": args.profile,
        "model": args.model,
        "doc_url": args.doc_url,
        "source_run_dir": str(run_dir.resolve()),
        "archive_dir": str(archive_dir.resolve()),
        "counts": counts,
        "tests": tests,
        "total_tests": total,
        "score": score,
        "summary_md": "summary.md",
        "summary_tsv": "summary.tsv",
        "summary_json": "summary.json",
    }
    return payload


def write_run_payload(archive_dir: Path, payload: dict) -> None:
    (archive_dir / "run.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def load_all_runs(site_dir: Path) -> list[dict]:
    runs = []
    for path in sorted((site_dir / "runs").glob("*/run.json")):
        try:
            runs.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    runs.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
    return runs


def status_badge(status: str) -> str:
    return f'<span class="badge badge-{html.escape(status)}">{html.escape(status)}</span>'


def latest_by_model(runs: list[dict]) -> list[dict]:
    latest = {}
    for run in runs:
        latest.setdefault(run["model"], run)
    return list(latest.values())


def aggregate_stats(runs: list[dict]) -> dict:
    models = sorted({run["model"] for run in runs})
    avg_score = round(sum(run.get("score", 0.0) for run in runs) / len(runs), 3) if runs else 0.0
    best_score = max((run.get("score", 0.0) for run in runs), default=0.0)
    return {
        "runs": len(runs),
        "models": len(models),
        "latest_models": len(latest_by_model(runs)),
        "avg_score": avg_score,
        "best_score": best_score,
    }


def details_to_pre(details: str) -> str:
    return f"<pre>{html.escape(details)}</pre>"


def overall_status(run: dict) -> str:
    counts = run.get("counts", {})
    if counts.get("FAIL", 0) or counts.get("TIMEOUT", 0):
        return "FAIL"
    if counts.get("PARTIAL", 0):
        return "PARTIAL"
    return "PASS"


def render_count_line(run: dict) -> str:
    counts = run.get("counts", {})
    return " / ".join(
        [
            f"P {counts.get('PASS', 0)}",
            f"Pt {counts.get('PARTIAL', 0)}",
            f"F {counts.get('FAIL', 0)}",
            f"T {counts.get('TIMEOUT', 0)}",
        ]
    )


def meta_block(title: str, description: str, canonical: str, site: dict, page_type: str, ld_json: dict) -> str:
    tags = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{html.escape(title)}</title>",
        f'<meta name="description" content="{html.escape(description, quote=True)}">',
        f'<meta name="keywords" content="{html.escape(", ".join(site.get("keywords", [])), quote=True)}">',
        '<meta name="robots" content="index,follow,max-image-preview:large">',
        f'<meta property="og:type" content="{html.escape(page_type)}">',
        f'<meta property="og:title" content="{html.escape(title, quote=True)}">',
        f'<meta property="og:description" content="{html.escape(description, quote=True)}">',
        f'<meta property="og:site_name" content="{html.escape(site["site_name"], quote=True)}">',
        f'<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{html.escape(title, quote=True)}">',
        f'<meta name="twitter:description" content="{html.escape(description, quote=True)}">',
    ]

    if canonical:
        tags.append(f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">')
        tags.append(f'<meta property="og:url" content="{html.escape(canonical, quote=True)}">')

    tags.append('<link rel="stylesheet" href="assets/dashboard.css">' if page_type == "website" else '<link rel="stylesheet" href="../../assets/dashboard.css">')
    tags.append(
        '<script type="application/ld+json">'
        + json.dumps(ld_json, indent=2)
        + "</script>"
    )
    return "\n  ".join(tags)


def trace_link(path: str) -> str:
    path = Path(path)
    if "traces" in path.parts:
        idx = path.parts.index("traces")
        return "/".join(path.parts[idx:])
    return path.name


def build_index_html(site: dict, runs: list[dict]) -> str:
    stats = aggregate_stats(runs)
    latest = latest_by_model(runs)
    latest_rows = "\n".join(
        f"""
        <tr>
          <td><a href="runs/{html.escape(run['run_id'])}/index.html">{html.escape(run['model'])}</a></td>
          <td>{status_badge(overall_status(run))}</td>
          <td class="mono">{html.escape(run['timestamp_pretty'])}</td>
          <td class="mono">{html.escape(run['mode'])}</td>
          <td class="mono">{run['score']:.2f}</td>
        </tr>
        """
        for run in latest
    )

    all_rows = "\n".join(
        f"""
        <tr>
          <td><a href="runs/{html.escape(run['run_id'])}/index.html">{html.escape(run['model'])}</a></td>
          <td>{status_badge(overall_status(run))}</td>
          <td class="mono">{html.escape(run['timestamp_pretty'])}</td>
          <td class="mono">{html.escape(run['mode'])}</td>
          <td class="mono">{html.escape(run['profile'])}</td>
          <td class="mono">{run['score']:.2f}</td>
          <td class="mono">{render_count_line(run)}</td>
        </tr>
        """
        for run in runs
    )

    title = f"{site['site_name']} | Public Ollama and Codex benchmark dashboard"
    description = site["site_description"]
    canonical = absolute_url(site, "index.html") or absolute_url(site, "")
    ld_json = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site["site_name"],
        "description": description,
        "url": site.get("site_url", ""),
        "about": [
            "Ollama",
            "Codex",
            "local LLM coding",
            "benchmarking",
        ],
    }

    repo_block = ""
    if site.get("repo_url"):
        repo_block = (
            f'<a class="hero-link" href="{html.escape(site["repo_url"])}">View the public GitHub repository</a>'
        )

    owner_line = html.escape(site["owner_name"])
    if site.get("owner_github"):
        owner_line = f'{owner_line} (<a href="https://github.com/{html.escape(site["owner_github"])}">@{html.escape(site["owner_github"])}</a>)'

    return f"""<!doctype html>
<html lang="en">
<head>
  {meta_block(title, description, canonical, site, "website", ld_json)}
</head>
<body>
  <main class="shell">
    <section class="hero">
      <p class="eyebrow">Public Ollama Codex Benchmark</p>
      <h1>{html.escape(site['site_tagline'])}</h1>
      <p class="subhead">{html.escape(description)}</p>
      <div class="meta-strip">
        <span class="pill">Runs archived: <strong>{stats['runs']}</strong></span>
        <span class="pill">Models tracked: <strong>{stats['models']}</strong></span>
        <span class="pill">Average score: <strong>{stats['avg_score']:.2f}</strong></span>
        <span class="pill">Best score seen: <strong>{stats['best_score']:.2f}</strong></span>
      </div>
      {repo_block}
    </section>

    <section class="grid stats">
      <article class="panel">
        <div class="stat-label">Total Runs</div>
        <div class="stat-value">{stats['runs']}</div>
      </article>
      <article class="panel">
        <div class="stat-label">Unique Models</div>
        <div class="stat-value">{stats['models']}</div>
      </article>
      <article class="panel">
        <div class="stat-label">Latest Model Snapshots</div>
        <div class="stat-value">{stats['latest_models']}</div>
      </article>
      <article class="panel">
        <div class="stat-label">Average Compatibility Score</div>
        <div class="stat-value">{stats['avg_score']:.2f}</div>
      </article>
    </section>

    <section class="section">
      <div class="grid info-grid">
        <article class="panel">
          <h2>What This Measures</h2>
          <p class="lede">This benchmark tracks how well local Ollama models cooperate with Codex for practical development work, not just chat quality.</p>
          <ul class="list">
            <li>File creation and file editing</li>
            <li>Terminal command execution and test runs</li>
            <li>Shell-based HTTP access for web-assisted tasks</li>
            <li>Dedicated Codex web-search behavior when requested</li>
          </ul>
        </article>
        <article class="panel">
          <h2>How To Reproduce</h2>
          <p class="lede">Each run page preserves the raw JSONL traces and summary artifacts so other developers can audit the exact behavior of the model.</p>
          <ul class="list">
            <li>Run <code>./codex-local-benchmark.sh --mode native-oss --model &lt;model&gt;</code></li>
            <li>Commit the generated <code>docs/</code> folder to GitHub</li>
            <li>Enable GitHub Pages for the <code>/docs</code> folder on your default branch</li>
          </ul>
        </article>
        <article class="panel">
          <h2>Ownership</h2>
          <p class="lede">Maintained by {owner_line}. The site is generated automatically after every benchmark run and is designed to publish cleanly on GitHub Pages.</p>
          <p class="kv">Search engines can index strong titles, descriptions, structured data, a sitemap, and stable run pages, but no implementation can guarantee a top result.</p>
        </article>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Latest by Model</h2>
          <p class="section-copy">The newest benchmark result for each Ollama model you have tested with Codex.</p>
        </div>
      </div>
      <div class="panel">
        <table>
          <thead>
            <tr>
              <th>Model</th>
              <th>Overall</th>
              <th>Last Run</th>
              <th>Mode</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {latest_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>All Runs</h2>
          <p class="section-copy">Each row links to a detail page with test outcomes, artifacts, and raw Codex traces.</p>
        </div>
      </div>
      <div class="panel">
        <table>
          <thead>
            <tr>
              <th>Model</th>
              <th>Overall</th>
              <th>Timestamp</th>
              <th>Mode</th>
              <th>Profile</th>
              <th>Score</th>
              <th>Counts</th>
            </tr>
          </thead>
          <tbody>
            {all_rows}
          </tbody>
        </table>
      </div>
      <p class="footer-note">Scores are computed as PASS = 1.0, PARTIAL = 0.5, FAIL/TIMEOUT = 0.0 across the benchmark tests. This makes the dashboard useful for tracking Codex and Ollama benchmark compatibility over time.</p>
    </section>
  </main>
</body>
</html>
"""


def build_run_html(site: dict, run: dict) -> str:
    test_rows = "\n".join(
        f"""
        <tr>
          <td><code>{html.escape(test['test'])}</code></td>
          <td>{status_badge(test['status'])}</td>
          <td>{details_to_pre(test['details'])}</td>
          <td><a href="{html.escape(trace_link(test['trace']))}">trace</a></td>
        </tr>
        """
        for test in run.get("tests", [])
    )

    title = f"{run['model']} benchmark results | {site['site_name']}"
    description = (
        f"Benchmark results for {run['model']} with Codex and Ollama, including "
        f"file-edit, shell, test, and web-search behavior from {run['timestamp_pretty']}."
    )
    canonical = absolute_url(site, f"runs/{run['run_id']}/index.html")
    ld_json = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": title,
        "datePublished": run["timestamp_iso"],
        "dateModified": run["timestamp_iso"],
        "author": {"@type": "Person", "name": site["owner_name"]},
        "about": [
            "Ollama",
            "Codex",
            run["model"],
            "benchmark",
        ],
        "url": canonical or "",
    }

    return f"""<!doctype html>
<html lang="en">
<head>
  {meta_block(title, description, canonical, site, "article", ld_json)}
</head>
<body>
  <main class="shell">
    <section class="hero">
      <p class="eyebrow">Benchmark Run</p>
      <h1>{html.escape(run['model'])}</h1>
      <p class="subhead">Run captured {html.escape(run['timestamp_pretty'])}. This page archives the exact benchmark summary and the raw Codex traces used to score the model.</p>
      <div class="meta-strip">
        <span class="pill">Overall: {status_badge(overall_status(run))}</span>
        <span class="pill">Mode: <strong>{html.escape(run['mode'])}</strong></span>
        <span class="pill">Profile: <strong>{html.escape(run['profile'])}</strong></span>
        <span class="pill">Score: <strong>{run['score']:.2f}</strong></span>
      </div>
      <a class="hero-link" href="../../index.html">Back to dashboard</a>
    </section>

    <section class="grid detail-grid">
      <article class="panel">
        <div class="stat-label">Source Run Directory</div>
        <div class="kv mono">{html.escape(run['source_run_dir'])}</div>
      </article>
      <article class="panel">
        <div class="stat-label">Counts</div>
        <div class="kv mono">{html.escape(render_count_line(run))}</div>
      </article>
      <article class="panel">
        <div class="stat-label">Ground Truth URL</div>
        <div class="kv"><a href="{html.escape(run['doc_url'])}">{html.escape(run['doc_url'])}</a></div>
      </article>
      <article class="panel">
        <div class="stat-label">Artifacts</div>
        <div class="kv">
          <a href="summary.md">summary.md</a><br>
          <a href="summary.tsv">summary.tsv</a><br>
          <a href="summary.json">summary.json</a><br>
          <a href="run.json">run.json</a>
        </div>
      </article>
    </section>

    <section class="section">
      <div class="section-head">
        <div>
          <h2>Test Results</h2>
          <p class="section-copy">Each test row links to the raw JSONL trace captured from Codex for this Ollama model benchmark run.</p>
        </div>
      </div>
      <div class="panel">
        <table>
          <thead>
            <tr>
              <th>Test</th>
              <th>Status</th>
              <th>Details</th>
              <th>Trace</th>
            </tr>
          </thead>
          <tbody>
            {test_rows}
          </tbody>
        </table>
      </div>
    </section>
  </main>
</body>
</html>
"""


def build_404_html(site: dict) -> str:
    title = f"Page not found | {site['site_name']}"
    description = "The requested benchmark page could not be found."
    canonical = absolute_url(site, "404.html")
    ld_json = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": canonical or "",
    }
    return f"""<!doctype html>
<html lang="en">
<head>
  {meta_block(title, description, canonical, site, "website", ld_json)}
</head>
<body>
  <main class="shell">
    <section class="hero">
      <p class="eyebrow">Not Found</p>
      <h1>That benchmark page does not exist.</h1>
      <p class="subhead">The path may have changed, but the dashboard homepage still has the full benchmark history.</p>
      <a class="hero-link" href="index.html">Back to dashboard</a>
    </section>
  </main>
</body>
</html>
"""


def build_robots_txt(site: dict) -> str:
    lines = [
        "User-agent: *",
        "Allow: /",
    ]
    sitemap_url = absolute_url(site, "sitemap.xml")
    if sitemap_url:
        lines.append(f"Sitemap: {sitemap_url}")
    return "\n".join(lines) + "\n"


def build_sitemap_xml(site: dict, runs: list[dict]) -> str:
    urls = []
    home_url = absolute_url(site, "index.html") or absolute_url(site, "")
    if home_url:
        urls.append((home_url, datetime.now(timezone.utc).isoformat()))
    for run in runs:
        url = absolute_url(site, f"runs/{run['run_id']}/index.html")
        if url:
            urls.append((url, run["timestamp_iso"]))

    body = "\n".join(
        "  <url>\n"
        f"    <loc>{xml_escape(loc)}</loc>\n"
        f"    <lastmod>{xml_escape(lastmod)}</lastmod>\n"
        "  </url>"
        for loc, lastmod in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n"
        "</urlset>\n"
    )


def public_site_data(site: dict, runs: list[dict]) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "site": {
            "site_name": site["site_name"],
            "site_tagline": site["site_tagline"],
            "site_description": site["site_description"],
            "site_url": site["site_url"],
            "repo_url": site["repo_url"],
            "owner_name": site["owner_name"],
            "owner_github": site["owner_github"],
            "keywords": site["keywords"],
        },
        "runs": runs,
    }


def render_site(site_dir: Path, site: dict, runs: list[dict]) -> None:
    assets_dir = site_dir / "assets"
    ensure_dir(assets_dir)
    (assets_dir / "dashboard.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (site_dir / "site-data.json").write_text(json.dumps(public_site_data(site, runs), indent=2) + "\n", encoding="utf-8")
    (site_dir / "index.html").write_text(build_index_html(site, runs), encoding="utf-8")
    (site_dir / "404.html").write_text(build_404_html(site), encoding="utf-8")
    (site_dir / "robots.txt").write_text(build_robots_txt(site), encoding="utf-8")
    (site_dir / "sitemap.xml").write_text(build_sitemap_xml(site, runs), encoding="utf-8")
    (site_dir / ".nojekyll").write_text("\n", encoding="utf-8")

    for run in runs:
        run_dir = site_dir / "runs" / run["run_id"]
        (run_dir / "index.html").write_text(build_run_html(site, run), encoding="utf-8")


def main():
    args = parse_args()
    run_dir = Path(args.run_dir).resolve()
    site_dir = Path(args.site_dir).resolve()
    ensure_dir(site_dir)

    summary_json = run_dir / "summary.json"
    if not summary_json.exists():
        raise SystemExit(f"Missing summary.json in {run_dir}")

    site = load_site_config(args.site_config)
    summary = load_summary(summary_json)
    run_id = resolve_run_id(site_dir, args.timestamp, args.mode, args.model, str(run_dir))
    archive_dir = site_dir / "runs" / run_id
    ensure_dir(archive_dir)

    copy_run_files(run_dir, archive_dir)
    payload = build_run_payload(args, run_dir, archive_dir, summary, run_id)
    write_run_payload(archive_dir, payload)

    runs = load_all_runs(site_dir)
    render_site(site_dir, site, runs)

    print(f"Published benchmark dashboard: {site_dir / 'index.html'}")


if __name__ == "__main__":
    main()
