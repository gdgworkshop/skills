#!/usr/bin/env python3
"""
Skills Companion for Google Antigravity (v1.2.0)
- Smart Environment Detector (Antigravity Web / Desktop Personal / Agent Platform)
- 5-Second Workspace Stack Auto-Loader (github.com/google/skills)
- Self-Updating Antigravity Educator & Live Google AI Tech Radar (g.dev/ai/googleaitech)
"""

import argparse
import json
import os
import platform
import re
import sys
import urllib.request
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

VERSION = "1.2.0"
REPO_RAW = "https://raw.githubusercontent.com/gdgworkshop/skills/main"
COMPANION_DIR = Path.home() / ".gemini" / "config" / "skills" / "skills-companion"
LOCAL_REPO_REFS = Path(__file__).resolve().parent.parent / "references"
SKILLS_ROOT = Path.home() / ".gemini" / "config" / "skills"
STATE_FILE = COMPANION_DIR / "state.json"
WORKSHOP_STATE_FILE = SKILLS_ROOT / "tokenmaxxing" / "state.json"

GA4_MEASUREMENT_ID = os.environ.get("SKILLS_COMPANION_GA4_ID", "G-J90GTZJF9E")
GA4_API_SECRET = os.environ.get("SKILLS_COMPANION_GA4_SECRET", "Q2mXTuXQTUuhIgYQtF-vwg")

SKILL_ALIASES = {
    "gemini": "gemini-api",
    "gemini-api": "gemini-api",
    "gemini-live": "gemini-live-api",
    "firebase": "firebase-basics",
    "firestore": "firebase-firestore",
    "crashlytics": "firebase-crashlytics",
    "remote-config": "firebase-remote-config-basics",
    "cloud-run": "cloud-run-basics",
    "cloudrun": "cloud-run-basics",
    "flutter": "flutter-apply-architecture-best-practices",
    "flutter-layout": "flutter-build-responsive-layout",
    "dart": "dart-run-static-analysis",
    "compose": "jetpack-compose-performance",
    "android": "android-profiler",
    "anr": "anr-audit-and-fix",
    "r8": "r8-analyzer",
    "gcloud": "gcloud",
}

SKILL_TRACKS = {
    "ai": ["gemini-api", "gemini-live-api"],
    "backend": ["firebase-basics", "firebase-firestore", "cloud-run-basics"],
    "cloud": ["cloud-run-basics"],
    "mobile": [
        "flutter-apply-architecture-best-practices",
        "flutter-build-responsive-layout",
        "dart-run-static-analysis",
    ],
    "android": ["jetpack-compose-performance", "anr-audit-and-fix", "android-profiler"],
}

MARKETPLACE_CARDS = {
    "gemini-api": "antigravity-plugins-official/plugin/gemini-api",
    "cloud-run-basics": "antigravity-plugins-official/plugin/google-cloud-developer",
    "android-profiler": "antigravity-plugins-official/plugin/android-cli-plugin",
    "jetpack-compose-performance": "antigravity-plugins-official/plugin/android-cli-plugin",
}


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            data.setdefault("seen_tips", [])
            data.setdefault("unlocked_features", [])
            data.setdefault("installed_skills", [])
            return data
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
    try:
        COMPANION_DIR.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except Exception:
        pass


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


def load_reference_json(filename: str, max_age_hours: int = 24):
    """
    Loads a lightweight JSON feed (2-6 KB). Refreshes from GitHub raw URL if cached copy
    is missing or older than max_age_hours, with instant offline fallback.
    """
    installed_path = COMPANION_DIR / "references" / filename
    local_path = LOCAL_REPO_REFS / filename
    candidate = installed_path if installed_path.exists() else local_path

    needs_refresh = True
    if candidate.exists():
        try:
            age = datetime.now(timezone.utc).timestamp() - candidate.stat().st_mtime
            if age < max_age_hours * 3600:
                needs_refresh = False
        except Exception:
            pass

    if needs_refresh and os.environ.get("SKILLS_COMPANION_OFFLINE") != "1":
        try:
            url = f"{REPO_RAW}/references/{filename}"
            req = urllib.request.Request(url, headers={"User-Agent": f"SkillsCompanion/{VERSION}"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                if resp.status == 200:
                    text = resp.read().decode("utf-8")
                    data = json.loads(text)
                    try:
                        installed_path.parent.mkdir(parents=True, exist_ok=True)
                        installed_path.write_text(text, encoding="utf-8")
                    except Exception:
                        pass
                    return data
        except Exception:
            pass

    if candidate.exists():
        try:
            return json.loads(candidate.read_text(encoding="utf-8"))
        except Exception:
            pass
    return None


def _has_active_workshop_credit() -> tuple:
    if not WORKSHOP_STATE_FILE.exists():
        return False, None
    try:
        ws = json.loads(WORKSHOP_STATE_FILE.read_text(encoding="utf-8"))
        project_id = ws.get("project_id")
        claimed_at = ws.get("claimed_at")
        if project_id and claimed_at:
            dt = datetime.fromisoformat(claimed_at.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) < dt + timedelta(hours=12):
                return True, project_id
    except Exception:
        pass
    return False, None


def detect_environment(override_mode: str = None) -> dict:
    sys_name = platform.system().lower()
    is_remote_container = bool(
        os.environ.get("ANTIGRAVITY_REMOTE")
        or os.environ.get("ANTIGRAVITY_WEB")
        or os.environ.get("ANTIGRAVITY_REMOTE_AGENT")
        or (sys_name == "linux" and not os.environ.get("DISPLAY") and (Path("/.dockerenv").exists() or os.environ.get("KUBERNETES_SERVICE_HOST")))
    )

    has_workshop, workshop_project = _has_active_workshop_credit()
    gcp_project = os.environ.get("GOOGLE_CLOUD_PROJECT") or workshop_project
    is_vertex_env = (
        os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() in ("1", "true", "yes")
        or os.environ.get("ANTIGRAVITY_AGENT_PLATFORM", "").lower() in ("1", "true", "yes")
        or has_workshop
    )

    if override_mode:
        m = override_mode.lower().strip()
        if m in ("web", "remote", "antigravity_web"):
            mode = "antigravity_web"
        elif m in ("cloud", "gcp", "workshop", "agent_platform"):
            mode = "agent_platform"
        else:
            mode = "desktop_personal"
    elif is_remote_container and not is_vertex_env:
        mode = "antigravity_web"
    elif is_vertex_env:
        mode = "agent_platform"
    else:
        mode = "desktop_personal"

    capabilities = {
        "official_skills_hub": True,
        "workspace_stack_scan": True,
        "antigravity_educator": True,
        "google_ai_tech_radar": True,
        "linkedin_builder_card": True,
        "local_skill_install": mode != "antigravity_web" or os.access(Path.home(), os.W_OK),
        "marketplace_card_nudges": mode in ("desktop_personal", "agent_platform"),
        "quota_radar_tips": mode in ("desktop_personal", "agent_platform"),
        "token_billing_receipts": mode == "agent_platform",
        "workshop_credit_wizard": mode == "agent_platform" and has_workshop,
        "local_os_browser_open": mode != "antigravity_web",
    }

    labels = {
        "antigravity_web": "🌐 Antigravity Web (Remote Agent — Skills-First Mode)",
        "desktop_personal": f"💻 Desktop / CLI ({sys_name.title()} — Personal Plan, Skills-First Mode)",
        "agent_platform": f"☁️ Agent Platform / GCP ({sys_name.title()} — Skills + Token Visibility)",
    }

    return {
        "mode": mode,
        "surface_key": "web" if mode == "antigravity_web" else ("cloud" if mode == "agent_platform" else "desktop"),
        "label": labels[mode],
        "os": sys_name,
        "is_web": mode == "antigravity_web",
        "is_agent_platform": mode == "agent_platform",
        "gcp_project": gcp_project,
        "has_active_workshop": has_workshop,
        "capabilities": capabilities,
    }


def get_installed_skills() -> set:
    installed = set()
    if SKILLS_ROOT.exists():
        for entry in SKILLS_ROOT.iterdir():
            if entry.is_dir() and (entry / "SKILL.md").exists():
                if entry.name not in ("skills-companion", "tokenmaxxing"):
                    installed.add(entry.name)
    return installed


def scan_workspace(cwd: Path = None) -> dict:
    root = cwd or Path.cwd()
    installed = get_installed_skills()
    detected_stacks = []
    recs = {}
    marketplace = set()

    def add_rec(skill: str, reason: str):
        if skill not in recs:
            recs[skill] = reason
        if skill in MARKETPLACE_CARDS:
            marketplace.add(MARKETPLACE_CARDS[skill])

    if (root / "firebase.json").exists() or (root / ".firebaserc").exists():
        detected_stacks.append("Firebase")
        add_rec("firebase-basics", "firebase.json detected")
        add_rec("firebase-firestore", "Firebase project detected")

    pubspec = root / "pubspec.yaml"
    if pubspec.exists():
        detected_stacks.append("Flutter / Dart")
        add_rec("flutter-apply-architecture-best-practices", "pubspec.yaml detected")
        add_rec("flutter-build-responsive-layout", "pubspec.yaml detected")
        add_rec("dart-run-static-analysis", "pubspec.yaml detected")
        try:
            txt = pubspec.read_text(encoding="utf-8", errors="ignore").lower()
            if "firebase" in txt or "cloud_firestore" in txt:
                add_rec("firebase-basics", "Firebase in pubspec.yaml")
                add_rec("firebase-firestore", "Firestore in pubspec.yaml")
            if "google_generative_ai" in txt or "firebase_ai" in txt or "gemini" in txt:
                add_rec("gemini-api", "Gemini SDK in pubspec.yaml")
        except Exception:
            pass

    for gradle in ("build.gradle.kts", "build.gradle", "app/build.gradle.kts", "app/build.gradle"):
        gp = root / gradle
        if gp.exists():
            if "Android" not in detected_stacks:
                detected_stacks.append("Android")
            add_rec("android-profiler", f"{gradle} detected")
            add_rec("anr-audit-and-fix", f"{gradle} detected")
            try:
                txt = gp.read_text(encoding="utf-8", errors="ignore").lower()
                if "compose" in txt:
                    add_rec("jetpack-compose-performance", f"Jetpack Compose in {gradle}")
                if "minifyenabled" in txt or "proguard" in txt:
                    add_rec("r8-analyzer", f"R8/Proguard in {gradle}")
            except Exception:
                pass

    for cloud_file in ("Dockerfile", "cloudbuild.yaml", "service.yaml"):
        if (root / cloud_file).exists():
            if "Containers / Cloud Run" not in detected_stacks:
                detected_stacks.append("Containers / Cloud Run")
            add_rec("cloud-run-basics", f"{cloud_file} detected")

    pkg = root / "package.json"
    if pkg.exists():
        try:
            txt = pkg.read_text(encoding="utf-8", errors="ignore").lower()
            fw = []
            for name, label in [("next", "Next.js"), ("react", "React"), ("vite", "Vite"), ("@angular", "Angular"), ("vue", "Vue"), ("express", "Express")]:
                if f'"{name}' in txt:
                    fw.append(label)
            detected_stacks.append(f"Node.js ({', '.join(fw)})" if fw else "Node.js / Web")
            if "@google/genai" in txt or "@google/generative-ai" in txt or "genkit" in txt:
                add_rec("gemini-api", "Google Gen AI SDK in package.json")
            if "firebase" in txt:
                add_rec("firebase-basics", "Firebase in package.json")
                add_rec("firebase-firestore", "Firebase in package.json")
            if fw:
                add_rec("cloud-run-basics", f"Web app ({fw[0]}) ready for 1-prompt deploy")
        except Exception:
            pass

    for pyf in ("requirements.txt", "pyproject.toml"):
        p = root / pyf
        if p.exists():
            if "Python" not in detected_stacks:
                detected_stacks.append("Python")
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore").lower()
                if "google-genai" in txt or "google-generativeai" in txt or "vertexai" in txt or "google-adk" in txt:
                    add_rec("gemini-api", f"Gemini/Vertex AI in {pyf}")
                if "firebase-admin" in txt or "google-cloud-firestore" in txt:
                    add_rec("firebase-firestore", f"Firestore in {pyf}")
                if any(web in txt for web in ("fastapi", "flask", "streamlit", "gradio", "uvicorn", "django")):
                    add_rec("cloud-run-basics", f"Python web service in {pyf}")
            except Exception:
                pass

    gomod = root / "go.mod"
    if gomod.exists():
        detected_stacks.append("Go")
        try:
            txt = gomod.read_text(encoding="utf-8", errors="ignore").lower()
            if "google.golang.org/genai" in txt:
                add_rec("gemini-api", "Gen AI SDK in go.mod")
            if "cloud.google.com/go" in txt:
                add_rec("cloud-run-basics", "Google Cloud SDK in go.mod")
        except Exception:
            pass

    recommendations = [
        {"skill": sk, "reason": reason, "installed": sk in installed}
        for sk, reason in recs.items()
    ]

    return {
        "workspace": str(root),
        "detected_stacks": detected_stacks,
        "installed_skills": sorted(installed),
        "recommendations": recommendations,
        "missing_skills": [r["skill"] for r in recommendations if not r["installed"]],
        "marketplace_plugins": sorted(marketplace),
    }


def install_single_skill(skill_name: str) -> bool:
    clean = SKILL_ALIASES.get(skill_name.lower().strip(), skill_name.lower().strip())
    categories = ["", "gemini/", "firebase/", "cloud/", "flutter/", "android/", "developers/"]
    target_dir = SKILLS_ROOT / clean

    for cat in categories:
        url = f"https://raw.githubusercontent.com/google/skills/main/skills/{cat}{clean}/SKILL.md"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": f"SkillsCompanion/{VERSION}"})
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


def cmd_tip(context_topic: str = None, override_mode: str = None, as_json: bool = False):
    env = detect_environment(override_mode)
    state = load_state()
    persona = state.get("persona") or "developer"
    catalog = load_reference_json("educator_catalog.json") or []

    eligible = [item for item in catalog if env["surface_key"] in item.get("surfaces", ["desktop", "cloud", "web"])]
    if not eligible:
        print("💡 Antigravity Tip: Try `/grill-me` before building to turn rough ideas into a clear architecture plan.")
        return

    chosen = None
    if context_topic:
        topic = context_topic.lower().strip()
        for item in eligible:
            if topic in item.get("contexts", []) or topic == item.get("id"):
                chosen = item
                break

    if not chosen:
        seen = set(state.get("seen_tips", []))
        unlocked = set(state.get("unlocked_features", []))
        unseen = [item for item in eligible if item["id"] not in seen and item["id"] not in unlocked]
        if not unseen:
            # Reset rotation cycle cleanly after user has seen all tips
            state["seen_tips"] = []
            unseen = [item for item in eligible if item["id"] not in unlocked] or eligible
        chosen = unseen[0]

    seen_list = state.get("seen_tips", [])
    if chosen["id"] not in seen_list:
        seen_list.append(chosen["id"])
        state["seen_tips"] = seen_list
        save_state(state)

    tip_text = chosen.get(persona) or chosen.get("developer")
    send_telemetry("educator_tip_shown", {"feature_id": chosen["id"], "context": context_topic or "rotation", "mode": env["mode"]})

    if as_json:
        print(json.dumps({"feature": chosen, "tip": tip_text, "persona": persona, "mode": env["mode"]}, indent=2))
        return

    print(tip_text)


def cmd_unlock(feature_id: str):
    clean = re.sub(r"[^a-zA-Z0-9_]", "_", feature_id.lower().strip().lstrip("/").replace("-", "_"))
    state = load_state()
    unlocked = set(state.get("unlocked_features", []))
    is_new = clean not in unlocked
    unlocked.add(clean)
    state["unlocked_features"] = sorted(unlocked)
    save_state(state)

    catalog = load_reference_json("educator_catalog.json") or []
    total = len(catalog) or 12
    send_telemetry("feature_adopted", {"feature_id": clean, "is_new": is_new})
    send_telemetry(f"feature_adopted_{clean}", {"feature_id": clean})

    print(f"🏆 Unlocked Antigravity Power Feature: `{clean}` ({len(unlocked)}/{total} mastered!)")


def cmd_whats_new(override_mode: str = None, as_json: bool = False):
    env = detect_environment(override_mode)
    state = load_state()
    changelog = load_reference_json("antigravity_changelog.json") or {}
    ai_updates = load_reference_json("google_ai_updates.json") or {}
    catalog = load_reference_json("educator_catalog.json") or []

    unlocked = state.get("unlocked_features", [])
    send_telemetry("whats_new_viewed", {"mode": env["mode"]})

    if as_json:
        print(json.dumps({
            "mode": env["mode"],
            "mastery": {"unlocked": unlocked, "total": len(catalog)},
            "antigravity_changelog": changelog,
            "google_ai_updates": ai_updates,
        }, indent=2))
        return

    print("=" * 68)
    print(" 🎓 WHAT'S NEW IN ANTIGRAVITY & GOOGLE AI")
    print("=" * 68)

    releases = changelog.get("releases", [])
    if releases:
        latest = releases[0]
        print(f"\n🚀 Latest Antigravity App Release: {latest.get('version')} ({latest.get('date')})")
        print(f"   {latest.get('headline')}")
        for h in latest.get("highlights", [])[:3]:
            print(f"   • {h[:140]}{'...' if len(h) > 140 else ''}")
        print(f"   Full changelog: {changelog.get('source', 'https://antigravity.google/docs/changelog')}")

    updates = ai_updates.get("updates", [])
    if updates:
        print("\n📡 Latest Google AI Tech (from g.dev/ai/googleaitech):")
        for u in updates[:6]:
            print(f"   • [{u.get('category')}] {u.get('title')} — {u.get('url')}")
        print("   Full deck: https://g.dev/ai/googleaitech")

    print(f"\n🏆 Your Antigravity Mastery: {len(unlocked)}/{len(catalog) or 12} power features unlocked")
    unseen_next = [c["command"] for c in catalog if c["id"] not in unlocked and env["surface_key"] in c.get("surfaces", [])][:3]
    if unseen_next:
        print(f"   Try next: {', '.join(unseen_next)}")
    print("=" * 68)


def cmd_init(override_mode: str = None, as_json: bool = False):
    env = detect_environment(override_mode)
    scan = scan_workspace()
    state = load_state()
    save_state(state)
    send_telemetry("skills_companion_init", {"mode": env["mode"], "stacks": len(scan["detected_stacks"])})

    if as_json:
        print(json.dumps({"version": VERSION, "environment": env, "workspace_scan": scan, "persona": state.get("persona")}, indent=2))
        return

    print("=" * 68)
    print(f" 🧩 SKILLS COMPANION FOR GOOGLE ANTIGRAVITY (v{VERSION})")
    print("=" * 68)
    print(f" Mode        : {env['label']}")
    print(f" Entry Point : https://g.dev/ai/agentskills")
    if env["is_agent_platform"] and env["gcp_project"]:
        print(f" GCP Project : {env['gcp_project']} (Token visibility enabled)")
    else:
        print(" Billing UI  : Auto-hidden (Skills & Educator focus)")

    print("\n 🔍 5-Second Workspace Scan:")
    if scan["detected_stacks"]:
        print(f"   Detected Stack : {', '.join(scan['detected_stacks'])}")
        for r in scan["recommendations"]:
            badge = "✅ Installed" if r["installed"] else "⬇️ Recommended"
            print(f"   • {r['skill']:<42} [{badge}] ({r['reason']})")
        if scan["missing_skills"]:
            print(f"\n   👉 Run `--scan --install` to install {len(scan['missing_skills'])} missing Google skill(s) in 1 click!")
    else:
        print("   No project files in current folder yet.")
        print("   Available curated tracks: `ai`, `backend`, `cloud`, `mobile`, `android`")

    if env["capabilities"]["marketplace_card_nudges"] and scan["marketplace_plugins"]:
        print("\n 🛒 Recommended Official Marketplace Plugins:")
        for mp in scan["marketplace_plugins"]:
            print(f"   • {mp}")

    print("=" * 68)


def cmd_scan(cwd: str = None, auto_install: bool = False, as_json: bool = False):
    target_path = Path(cwd).expanduser().resolve() if cwd else Path.cwd()
    scan = scan_workspace(target_path)
    send_telemetry("skills_companion_scan", {"matches": len(scan["recommendations"]), "auto_install": auto_install})

    if as_json:
        print(json.dumps(scan, indent=2))
        return

    print(f"🔍 Workspace Scan: {scan['workspace']}")
    if not scan["recommendations"]:
        print("   No Google stack manifests detected here yet.")
        print("   Tip: Install a starter track with `--install-skill ai` or `--install-skill backend`.")
        return

    print(f"   Stacks detected: {', '.join(scan['detected_stacks'])}")
    for r in scan["recommendations"]:
        status = "✅ Already installed" if r["installed"] else "⬇️ Ready to install"
        print(f"   • {r['skill']} — {status} ({r['reason']})")

    if auto_install and scan["missing_skills"]:
        print(f"\n📦 Installing {len(scan['missing_skills'])} recommended official Google skill(s)...")
        for sk in scan["missing_skills"]:
            install_single_skill(sk)
    elif auto_install:
        print("\n✨ All recommended official Google skills for this project are already installed!")


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
    parser.add_argument("--path", type=str, help="Optional workspace directory to scan")
    parser.add_argument("--install", action="store_true", help="When combined with --scan, installs missing recommended skills")
    parser.add_argument("--mode", type=str, choices=["web", "desktop", "cloud"], help="Override detected environment mode")
    parser.add_argument("--persona", type=str, help="Set persona (developer or builder)")
    parser.add_argument("--install-skill", dest="install_skill", type=str, help="Install official Google skill or track")
    parser.add_argument("--whats-new", dest="whats_new", action="store_true", help="Show latest Antigravity & Google AI updates")
    parser.add_argument("--tip", action="store_true", help="Show a smart, non-repeating Antigravity Educator tip")
    parser.add_argument("--context", type=str, help="Contextual trigger for --tip (e.g. refactor, side_question, brainstorm, long_thread, debug, frontend)")
    parser.add_argument("--unlock", type=str, help="Record adoption of an Antigravity power feature (e.g. swarm, btw, teamwork)")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    args = parser.parse_args()

    if args.scan:
        cmd_scan(cwd=args.path, auto_install=args.install, as_json=args.json)
    elif args.persona:
        cmd_persona(args.persona)
    elif args.install_skill:
        target = args.install_skill.lower().strip()
        if target in SKILL_TRACKS:
            for sk in SKILL_TRACKS[target]:
                install_single_skill(sk)
        else:
            install_single_skill(target)
    elif args.whats_new:
        cmd_whats_new(override_mode=args.mode, as_json=args.json)
    elif args.tip:
        cmd_tip(context_topic=args.context, override_mode=args.mode, as_json=args.json)
    elif args.unlock:
        cmd_unlock(args.unlock)
    else:
        cmd_init(override_mode=args.mode, as_json=args.json)


if __name__ == "__main__":
    main()
