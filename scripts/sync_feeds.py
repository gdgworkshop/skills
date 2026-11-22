#!/usr/bin/env python3
"""
sync_feeds.py — Daily auto-sync for Skills Companion (v1.2.0)
Converts:
  1. https://antigravity.google/docs/changelog.md  -> references/antigravity_changelog.json (~3 KB)
  2. https://g.dev/ai/googleaitech                 -> references/google_ai_updates.json (~4 KB)
So every Antigravity Desktop & Web user gets instant, always-fresh updates in <100ms
without downloading 37MB Google Slides HTML.
"""

import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS_DIR = ROOT / "references"
REFS_DIR.mkdir(parents=True, exist_ok=True)


def fetch_text(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "SkillsCompanionFeedSync/1.2"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def sync_antigravity_changelog() -> dict:
    md = fetch_text("https://antigravity.google/docs/changelog.md")
    app_section_match = re.search(r"## Antigravity App(.*?)(?:\n## |\Z)", md, re.S)
    section = app_section_match.group(1) if app_section_match else md[:12000]

    # Split by version headings like ### [v2.34.0](...)
    blocks = re.split(r"\n(?=### \[v)", section)
    releases = []
    for block in blocks:
        ver_m = re.search(r"### \[(v[0-9\.]+)\]", block)
        if not ver_m:
            continue
        version = ver_m.group(1)
        lines = [l.strip() for l in block.splitlines() if l.strip()]

        date_str = ""
        headline = ""
        for line in lines[1:8]:
            if re.match(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}$", line):
                date_str = line
            elif line.startswith("### ") and not line.startswith("### [v"):
                headline = line.replace("### ", "").strip()

        improvements = []
        in_imp = False
        for line in lines:
            if "**Improvements:**" in line or "**New:**" in line:
                in_imp = True
                continue
            if "**Fixes:**" in line:
                break
            if in_imp and (line.startswith("* ") or line.startswith("- ")):
                item = re.sub(r"^[\*\-]\s+", "", line).strip()
                if item:
                    improvements.append(item)

        releases.append({
            "version": version,
            "date": date_str,
            "headline": headline or f"Antigravity {version}",
            "highlights": improvements[:5],
        })
        if len(releases) >= 3:
            break

    payload = {
        "source": "https://antigravity.google/docs/changelog",
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "releases": releases,
    }
    (REFS_DIR / "antigravity_changelog.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def _classify_and_title(url: str) -> tuple:
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")
    slug = path.split("/")[-1] if path else host

    if "antigravity.google" in host:
        cat = "Antigravity"
    elif "adk" in host or "adk-python" in path:
        cat = "Agent Development Kit (ADK)"
    elif "firebase" in host:
        cat = "Firebase"
    elif "bigquery" in path:
        cat = "BigQuery AI"
    elif "cloud.google.com/run" in url or "/run/" in path:
        cat = "Cloud Run"
    elif "stitch.google" in host or "stitch" in path:
        cat = "Google Labs"
    elif "gemma" in path:
        cat = "Gemma"
    elif "aistudio.google.com" in host or "gemini" in path or "genie" in path:
        cat = "Gemini API"
    else:
        cat = "Google AI"

    # Build a clean title from the last meaningful path segment
    parts = [p for p in path.split("/") if p and p not in ("docs", "overview", "release-notes", "tag", "releases")]
    raw_name = parts[-1] if parts else slug
    if "release-notes" in path:
        raw_name = f"{cat} Release Notes"
    elif "v2." in slug or re.match(r"^v\d+\.\d+", slug):
        raw_name = f"{cat} {slug}"
    else:
        raw_name = raw_name.replace("-", " ").replace("_", " ").title()
        raw_name = raw_name.replace("Ai", "AI").replace("Mcp", "MCP").replace("Gpu", "GPU").replace("Api", "API").replace("Adk", "ADK")

    return cat, raw_name


def sync_google_ai_tech() -> dict:
    raw = fetch_text("https://g.dev/ai/googleaitech", timeout=25)
    decoded = raw.replace("\\x3d", "=").replace("\\x22", '"').replace("\\x26", "&").replace("\\/", "/")
    links = re.findall(r'https://www\.google\.com/url\?q=([^&"]+)', decoded)

    skip_exact = {
        "https://g.dev/ai/build",
        "https://g.dev/ai/googleaitech-copy",
        "https://antigravity.google",
        "https://antigravity.google/download",
        "https://antigravity.google/docs/changelog",
        "https://aistudio.google.com",
        "https://aistudio.google.com/apps",
        "https://aistudio.google.com/docs/changelog",
        "https://blog.google/technology/developers",
        "https://research.google/blog",
        "https://cloud.google.com/run/docs",
    }

    updates = []
    seen_urls = set()
    seen_titles = set()
    for l in links:
        u = urllib.parse.unquote(l).rstrip("/")
        if u in seen_urls or u in skip_exact:
            continue
        if any(skip in u for skip in ("docs.google.com/presentation", "youtube.com", "twitter.com", "x.com", "linkedin.com")):
            continue
        if "release-notes" in u and len(updates) >= 8:
            continue

        cat, title = _classify_and_title(u)
        if len(title) < 4 or title.lower() in seen_titles:
            continue

        seen_urls.add(u)
        seen_titles.add(title.lower())
        updates.append({
            "category": cat,
            "title": title,
            "url": u,
        })
        if len(updates) >= 15:
            break

    payload = {
        "source": "https://g.dev/ai/googleaitech",
        "handbook": "https://g.dev/ai/build",
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "updates": updates,
    }
    (REFS_DIR / "google_ai_updates.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


if __name__ == "__main__":
    cl = sync_antigravity_changelog()
    print(f"✅ Synced {len(cl['releases'])} Antigravity releases → references/antigravity_changelog.json")
    ai = sync_google_ai_tech()
    print(f"✅ Synced {len(ai['updates'])} Google AI updates → references/google_ai_updates.json")
