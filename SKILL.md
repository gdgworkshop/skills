---
name: skills-companion
description: Universal Skills Companion for Google Antigravity (Desktop, CLI, IDE, and Web at antigravity.google.com). Automatically detects Web vs. Desktop vs. Agent Platform, scans workspaces in 5 seconds to install verified Official Google Agent Skills (github.com/google/skills), coaches on new Antigravity features (/swarm, /btw, /teamwork, /grill-me, /compact), syncs latest Google AI updates (g.dev/ai/googleaitech), and generates shareable LinkedIn Builder Cards.
---

# Skills Companion for Google Antigravity (v1.1.0)

## 1. Smart Environment & Plan Detection
Run `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --init --json` (on Desktop/CLI/Remote with shell) or evaluate context directly on Web to activate the exact right capability profile:

| Mode | When Active | Enabled | Auto-Disabled |
| :--- | :--- | :--- | :--- |
| **`antigravity_web`** | Running on `antigravity.google.com` Remote Agent (personal Pro/Ultra) | Official Google Skills Hub, Stack Auto-Scan, Live Educator, Dual-Mode Gemini SDK, LinkedIn Builder Card | `$5` voucher setup, dollar/token receipts, local OS browser openers (`open` / `start`) |
| **`desktop_personal`** | Desktop App / CLI / IDE on Personal Pro, Ultra, or Free | Everything in Web **+** Local skill install, Quota awareness, Marketplace `<plugin-card>` nudges | `$5` voucher setup, dollar/token billing receipts |
| **`agent_platform`** | Google Cloud Agent Platform / Vertex AI / Active Workshop Grant | Everything in Desktop **+** Vertex AI Project ID auto-injection, live token visibility (`g.dev/ai/workshop`) | *(All capabilities enabled)* |

## 2. Zero-Install Web Mode (`antigravity.google.com`)
If `~/.gemini/config/skills/skills-companion` is unavailable or non-persistent in an ephemeral remote session:
1. Do **NOT** fail or tell the user to run `open -g` / `$5` credit steps.
2. Inspect the current workspace directly using your file-reading tools and apply the **Stack-to-Skill Matrix** below.
3. Fetch matching official blueprints on demand from `https://raw.githubusercontent.com/google/skills/main/skills/<category>/<skill>/SKILL.md` and follow them directly in-session.

## 3. 5-Second Workspace Stack-to-Skill Matrix
| Detected Manifest / Dependency | Official Google Skills to Load | Optional Marketplace Plugin |
| :--- | :--- | :--- |
| `firebase.json`, `.firebaserc`, `firebase` pkg | `firebase-basics`, `firebase-firestore` | — |
| `pubspec.yaml` (Flutter / Dart) | `flutter-apply-architecture-best-practices`, `flutter-build-responsive-layout`, `dart-run-static-analysis` | — |
| `build.gradle(.kts)` (Android / Compose) | `jetpack-compose-performance`, `anr-audit-and-fix`, `android-profiler`, `r8-analyzer` | `antigravity-plugins-official/plugin/android-cli-plugin` |
| `@google/genai`, `google-genai`, `vertexai`, `google-adk` | `gemini-api`, `gemini-live-api` | `antigravity-plugins-official/plugin/gemini-api` |
| `Dockerfile`, `cloudbuild.yaml`, Next/React/FastAPI/Flask | `cloud-run-basics` | `antigravity-plugins-official/plugin/google-cloud-developer` |

## 4. Interactive First-Launch Onboarding (`g.dev/ai/agentskills`)
When a user launches `https://g.dev/ai/agentskills`, ALWAYS call `ask_question` in the same turn with 2 questions:
1. **"How should I tailor explanations and code guidance for you?"**
   - `(Recommended) 💻 Pro Developer (concise diffs, architecture patterns & CLI)`
   - `👷 Vibe Coder / Builder (intuitive visual explanations, zero terminal jargon)`
2. **"What would you like to do first?"**
   - `(Recommended) 🔍 Scan my project & install the best official Google Agent Skills`
   - `🎓 Show me what's new in Antigravity (/swarm, /btw, /teamwork, MCP Apps)`
   - `📡 Show me the latest Google AI launches (g.dev/ai/googleaitech)`
   - `🏆 Generate my Antigravity Builder Card for LinkedIn`

## 5. CLI Commands (Desktop / Terminal)
- Detect environment + scan workspace: `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --init`
- Scan & auto-install missing official skills for current repo: `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --scan --install`
- Test any environment mode explicitly: `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --init --mode <web|desktop|cloud>`
- Save persona: `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --persona <developer|builder>`
- Install a specific skill or track (`ai`, `backend`, `cloud`, `mobile`, `android`): `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --install-skill <name_or_track>`
