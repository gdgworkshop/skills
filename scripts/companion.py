#!/usr/bin/env python3
"""
Skills Companion for Google Antigravity (v1.0.0)
Universal skills loader, environment detector, and Antigravity feature co-pilot
for Desktop, CLI, IDE Extensions, and Antigravity Web (antigravity.google.com).
"""

import argparse
import json
import os
import platform
import re
import sys
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

VERSION = "1.0.0"
COMPANION_DIR = Path.home() / ".gemini" / "config" / "skills" / "skills-companion"
STATE_FILE = COMPANION_DIR / "state.json"

GA4_MEASUREMENT_ID = os.environ.get("SKILLS_COMPANION_GA4_ID", "G-J90GTZJF9E")
GA4_API_SECRET = os.environ.get("SKILLS_COMPANION_GA4_SECRET", "Q2mXTuXQTUuhIgYQtF-vwg")

SKILL_ALIASES = {
    "gemini": "gemini-api",
    "gemini-api": "gemini-api",
    "gemini-live": "gemini-live-api",
    "firebase": "firebase-basics",
    "firestore": "firebase-firestore",
    "crashlytics": "firebase-crashlytics",
    "cloud-run": "cloud-run-basics",
    "cloudrun": "cloud-run-basics",
    "flutter": "flutter-apply-architecture-best-practices",
    "compose": "jetpack-compose-performance",
    "android": "android-profiler",
}

SKILL_TRACKS = {
    "ai": ["gemini-api", "gemini-live-api"],
    "backend": ["firebase-basics", "firebase-firestore", "cloud-run-basics"],
    "cloud": ["cloud-run-basics"],
    "mobile": ["flutter-apply-architecture-best-practices", "flutter-build-responsive-layout"],
}

STACK_SIGNATURES = [
    ("firebase.json", ["firebase-basics", "firebase-firestore"], "Firebase"),
    ("pubspec.yaml", ["flutter-apply-architecture-best-practices", "flutter-build-responsive-layout"], "Flutter"),
    ("Dockerfile", ["cloud-run-basics"], "Docker / Cloud Run"),
    ("build.gradle.kts", ["jetpack-compose-performance"], "Android / Jetpack Compose"),
]


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "client_id": str(uuid.uuid4()),
        "persona": None,
        "installed_skills": [],
        "seen_tips": [],
        "unlocked_features": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def save_state(state: dict):
    COMPANION_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def send_telemetry(event_name: str, params: dict = None):
    if os.environ.get("DO_NOT_TRACK") == "1" or os.environ.get("SKILLS_COMPANION_NO_TELEMETRY") == "1":
        return
    try:
        state = load_state()
        cid = state.get("client_id") or str(uuid.uuid4())
        event_params = {"entry_surface": "agentskills", "companion_version": VERSION}
        if params:
            event_params.update(params)
        payload = json.dumps({
            "client_id": cid,
            "events": [{"name": event_name, "params": event_params}],
        }).encode("utf-8")
        url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA4_MEASUREMENT_ID}&api_secret={GA4_API_SECRET}"
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass


def detect_environment() -> dict:
    sys_name = platform.system().lower()
    is_remote_web = bool(
        os.environ.get("ANTIGRAVITY_REMOTE")
        or os.environ.get("ANTIGRAVITY_WEB")
        or (sys_name == "linux" and not os.environ.get("DISPLAY") and Path("/.dockerenv").exists())
    )
    surface = "antigravity_web" if is_remote_web else f"desktop_{sys_name}"
    return {
        "surface": surface,
        "is_web": is_remote_web,
        "os": sys_name,
    }


def scan_workspace(cwd: Path = None) -> list:
    root = cwd or Path.cwd()
    recommendations = []
    seen = set()

    for filename, skills, label in STACK_SIGNATURES:
        if (root / filename).exists():
            for sk in skills:
                if sk not in seen:
                    seen.add(sk)
                    recommendations.append((sk, label))

    # Inspect package.json / requirements.txt for google-genai or firebase
    for dep_file in ("package.json", "requirements.txt", "pyproject.toml"):
        p = root / dep_file
        if p.exists():
            try:
                content = p.read_text(encoding="utf-8", errors="ignore").lower()
                if "google-genai" in content or "@google/genai" in content:
                    if "gemini-api" not in seen:
                        seen.add("gemini-api")
                        recommendations.append(("gemini-api", f"Gemini SDK ({dep_file})"))
                if "firebase" in content:
                    if "firebase-basics" not in seen:
                        seen.add("firebase-basics")
                        recommendations.append(("firebase-basics", f"Firebase ({dep_file})"))
            except Exception:
                pass

    return recommendations


def install_single_skill(skill_name: str) -> bool:
    clean = SKILL_ALIASES.get(skill_name.lower().strip(), skill_name.lower().strip())
    categories = ["", "gemini/", "firebase/", "cloud/", "flutter/", "android/", "developers/"]
    target_dir = Path.home() / ".gemini" / "config" / "skills" / clean

    for cat in categories:
        url = f"https://raw.githubusercontent.com/google/skills/main/skills/{cat}{clean}/SKILL.md"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SkillsCompanion/1.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                if resp.status == 200:
                    content = resp.read().decode("utf-8")
                    target_dir.mkdir(parents=True, exist_ok=True)
                    (target_dir / "SKILL.md").write_text(content, encoding="utf-8")
                    state = load_state()
                    installed = set(state.get("installed_skills", []))
                    installed.add(clean)
                    state["installed_skills"] = sorted(installed)
                    save_state(state)
                    s_slug = re.sub(r"[^a-zA-Z0-9_]", "_", clean)
                    send_telemetry("skill_installed", {"skill": clean})
                    send_telemetry(f"skill_installed_{s_slug}", {"skill": clean})
                    print(f"✅ Installed official Google skill '{clean}' → {target_dir}")
                    return True
        except Exception:
            continue

    print(f"⚠️ Could not locate '{clean}' on github.com/google/skills. Browse: https://github.com/google/skills")
    return False


def cmd_init():
    env = detect_environment()
    state = load_state()
    save_state(state)
    send_telemetry("skills_companion_init", {"surface": env["surface"]})

    print("=" * 64)
    print(f" 🧩 SKILLS COMPANION FOR GOOGLE ANTIGRAVITY (v{VERSION})")
    print("=" * 64)
    mode_label = "🌐 Antigravity Web (Remote Mode)" if env["is_web"] else f"💻 Desktop / CLI ({env['os'].title()})"
    print(f" Environment : {mode_label}")
    print(f" Entry Point : https://g.dev/ai/agentskills")

    recs = scan_workspace()
    if recs:
        print("\n 🔍 Detected Workspace Stack:")
        for sk, label in recs:
            print(f"   • {label} → recommended skill: `{sk}`")
    else:
        print("\n 🔍 Workspace Scan: Ready to load official Google skills anytime.")

    print("\n 💡 Next: Confirm persona & goal via interactive prompt.")
    print("=" * 64)


def cmd_scan():
    recs = scan_workspace()
    send_telemetry("skills_companion_scan", {"matches": len(recs)})
    if not recs:
        print("🔍 No specific Google stack files detected in this folder yet.")
        print("   Try installing a curated track: `ai`, `backend`, `cloud`, or `mobile`.")
        return
    print("🔍 Recommended Official Google Agent Skills for this workspace:")
    for sk, label in recs:
        print(f"  • {sk}  (detected from {label})")


def cmd_persona(role: str):
    norm = "builder" if role.lower() in ("builder", "vibe", "vibe-coder", "vibecoder") else "developer"
    state = load_state()
    state["persona"] = norm
    save_state(state)
    send_telemetry("persona_selected", {"role": norm})
    label = "👷 Vibe Coder / Builder" if norm == "builder" else "💻 Pro Developer"
    print(f"✅ Persona saved: {label}")


def main():
    parser = argparse.ArgumentParser(description="Skills Companion for Google Antigravity")
    parser.add_argument("--init", action="store_true", help="Initialize Skills Companion and detect environment")
    parser.add_argument("--scan", action="store_true", help="Scan workspace and recommend official Google skills")
    parser.add_argument("--persona", type=str, help="Set persona (developer or builder)")
    parser.add_argument("--install-skill", dest="install_skill", type=str, help="Install official Google skill or track")
    parser.add_argument("--status", action="store_true", help="Show companion status")
    args = parser.parse_args()

    if args.init:
        cmd_init()
    elif args.scan:
        cmd_scan()
    elif args.persona:
        cmd_persona(args.persona)
    elif args.install_skill:
        target = args.install_skill.lower().strip()
        if target in SKILL_TRACKS:
            for sk in SKILL_TRACKS[target]:
                install_single_skill(sk)
        else:
            install_single_skill(target)
    else:
        cmd_init()


if __name__ == "__main__":
    main()
