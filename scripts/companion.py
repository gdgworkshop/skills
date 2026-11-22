#!/usr/bin/env python3
"""
Skills Companion for Google Antigravity (v1.1.0)
Smart Environment Detector (Web / Desktop / Agent Platform) + 5-Second Workspace
Stack Auto-Loader for Official Google Agent Skills (github.com/google/skills).
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

VERSION = "1.1.0"
COMPANION_DIR = Path.home() / ".gemini" / "config" / "skills" / "skills-companion"
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


def _has_active_workshop_credit() -> tuple:
    """Checks passively (documented local state file) if user has an active GCP workshop session."""
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
    """
    Smart, sandbox-safe environment & plan detector.
    Returns one of 3 clean capability profiles:
      1. antigravity_web   (antigravity.google.com Remote Agent — personal Pro/Ultra only)
      2. desktop_personal  (Antigravity Desktop / CLI / IDE on Personal Pro/Ultra/Free)
      3. agent_platform    (Google Cloud Agent Platform / Vertex AI / Active Workshop Grant)
    """
    sys_name = platform.system().lower()
    is_remote_container = bool(
        os.environ.get("ANTIGRAVITY_REMOTE")
        or os.environ.get("ANTIGRAVITY_WEB")
        or os.environ.get("ANTIGRAVITY_REMOTE_AGENT")
        or (sys_name == "linux" and not os.environ.get("DISPLAY") and (Path("/.dockerenv").exists() or os.environ.get("KUBERNETES_SERVICE_HOST")))
    )

    # Check documented Agent Platform / Vertex AI / Workshop signals
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

    # Build capability matrix strictly based on detected mode
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
    """
    5-second smart workspace stack scanner.
    Inspects standard manifest files to recommend exact official Google Agent Skills
    and official Antigravity Marketplace plugins.
    """
    root = cwd or Path.cwd()
    installed = get_installed_skills()
    detected_stacks = []
    recs = {}  # skill_name -> reason
    marketplace = set()

    def add_rec(skill: str, reason: str):
        if skill not in recs:
            recs[skill] = reason
        if skill in MARKETPLACE_CARDS:
            marketplace.add(MARKETPLACE_CARDS[skill])

    # 1. Firebase
    if (root / "firebase.json").exists() or (root / ".firebaserc").exists():
        detected_stacks.append("Firebase")
        add_rec("firebase-basics", "firebase.json detected")
        add_rec("firebase-firestore", "Firebase project detected")

    # 2. Flutter / Dart
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

    # 3. Android / Kotlin / Jetpack Compose
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

    # 4. Docker / Cloud Run
    for cloud_file in ("Dockerfile", "cloudbuild.yaml", "service.yaml"):
        if (root / cloud_file).exists():
            if "Containers / Cloud Run" not in detected_stacks:
                detected_stacks.append("Containers / Cloud Run")
            add_rec("cloud-run-basics", f"{cloud_file} detected")

    # 5. Node / JS / TS (package.json)
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

    # 6. Python (requirements.txt / pyproject.toml)
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

    # 7. Go (go.mod)
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

    recommendations = []
    for sk, reason in recs.items():
        recommendations.append({
            "skill": sk,
            "reason": reason,
            "installed": sk in installed,
        })

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
    parser.add_argument("--mode", type=str, choices=["web", "desktop", "cloud"], help="Override detected environment mode for testing")
    parser.add_argument("--persona", type=str, help="Set persona (developer or builder)")
    parser.add_argument("--install-skill", dest="install_skill", type=str, help="Install official Google skill or track")
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
    else:
        cmd_init(override_mode=args.mode, as_json=args.json)


if __name__ == "__main__":
    main()
