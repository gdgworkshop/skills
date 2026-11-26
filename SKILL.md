---
name: skills-companion
description: Universal Skills Companion for Google Antigravity (Desktop, CLI, IDE, and Web at antigravity.google.com) plus zero-warning support for Claude Code, Cursor, and Codex. Auto-detects workspaces or guides new ideas from prompt to Cloud Run with hard $5 scale-to-zero guardrails, lazy-loads verified Official Google Agent Skills (github.com/google/skills), coaches on Antigravity features (/swarm, /btw, /teamwork, /grill-me, /compact), syncs g.dev/ai/googleaitech, and generates LinkedIn Builder Cards.
---

# Skills Companion for Google Antigravity (v1.4.0)

## 1. Smart Environment & Plan Detection
Run `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --init --json` (on Antigravity Desktop/CLI/IDE) or evaluate context directly on Web / Cross-IDE harnesses:

| Mode | When Active | Enabled | Auto-Disabled |
| :--- | :--- | :--- | :--- |
| **`antigravity_web`** | Running on `antigravity.google.com` Remote Agent (personal Pro/Ultra) | Official Google Skills Hub, Idea-to-Cloud-Run Build Flow, Stack Scan, Live Educator, LinkedIn Builder Card | `$5` voucher option, dollar/token receipts, local OS browser openers (`open` / `start`) |
| **`desktop_personal`** | Desktop App / CLI / IDE on Personal Pro, Ultra, or Free | Everything in Web **+** Local skill install, Quota awareness, Marketplace `<plugin-card>` nudges, **On-Demand `$5` Event Credit Bridge (Q2 option)** | Automatic dollar/token billing receipts |
| **`agent_platform`** | Google Cloud Agent Platform / Vertex AI / Active Workshop Grant | Everything in Desktop **+** Vertex AI Project ID auto-injection, live token visibility (`g.dev/ai/workshop`) | *(All capabilities enabled)* |
| **`cross_ide`** | Running in **Claude Code, Cursor, Codex, or Windsurf** | **Zero `curl \| bash`!** Use `npx skills add google/skills`, Idea-to-Cloud-Run Build Flow, `$5` Scale-to-Zero Guardrails, LinkedIn Builder Card URL | Antigravity-only slash tips, shell installer scripts, dotfile edits |

## 2. Zero-Install Web Mode (`antigravity.google.com`) & Cross-IDE Mode
- **On Antigravity Web:** Do **NOT** run `open -g` or `$5` credit steps. Inspect the workspace directly or start the Idea-to-Cloud-Run flow, and fetch only the needed `SKILL.md` from `https://raw.githubusercontent.com/google/skills/main/skills/<category>/<skill>/SKILL.md` into session context.
- **On Claude Code / Cursor / Codex / Windsurf:** Never run `curl | bash` or modify global shell dotfiles. Equip official Google skills transparently via `npx skills add google/skills` (selecting only the skills needed for the project), then follow Sections 3 & 5 below.

## 3. Hard $5 Scale-to-Zero Guardrails & Lazy Skill Loading
Apply these silent engineering guardrails on every Google Cloud build:
1. **Scale-to-Zero & Budget-Safe Defaults ($5 Cap):**
   - Prefer **Cloud Run (`--min-instances=0`)**, **Firestore free tier**, **Cloud Storage**, **Firebase Hosting** (for static sites), and **Flash-class Gemini models** by default.
   - **Warn explicitly before provisioning always-on / hourly-billed services** (e.g., Cloud SQL, GKE clusters, always-on VMs, managed VPC connectors) that could burn a `$5` event credit or surprise a personal account—offer a scale-to-zero alternative first.
   - Use **least-privilege IAM** (avoid Owner / default compute SA when creating production configs) and never hardcode secrets or API keys.
2. **Lazy Skill Loading (Keep Context Fast & Lean):**
   - **Never load all Google skills into context up front.** Load each official `SKILL.md` only when its specific phase starts (e.g., load `gemini-api` while wiring AI, load `cloud-run-basics` only when ready to deploy).

## 4. 5-Second Workspace Stack-to-Skill Matrix
| Detected Manifest / Dependency | Official Google Skills to Load (Lazily) | Optional Marketplace Plugin |
| :--- | :--- | :--- |
| `firebase.json`, `.firebaserc`, `firebase` pkg | `firebase-basics`, `firebase-firestore` | — |
| `pubspec.yaml` (Flutter / Dart) | `flutter-apply-architecture-best-practices`, `flutter-build-responsive-layout`, `dart-run-static-analysis` | — |
| `build.gradle(.kts)` (Android / Compose) | `jetpack-compose-performance`, `anr-audit-and-fix`, `android-profiler`, `r8-analyzer` | `antigravity-plugins-official/plugin/android-cli-plugin` |
| `@google/genai`, `google-genai`, `vertexai`, `google-adk` | `gemini-api`, `gemini-live-api` | `antigravity-plugins-official/plugin/gemini-api` |
| `Dockerfile`, `cloudbuild.yaml`, Next/React/FastAPI/Flask | `cloud-run-basics` | `antigravity-plugins-official/plugin/google-cloud-developer` |

## 5. Interactive First-Launch Onboarding (`g.dev/ai/agentskills`)
When a user launches `https://g.dev/ai/agentskills`, ALWAYS call `ask_question` in the same turn with 2 questions:
1. **"How should I tailor explanations and code guidance for you?"**
   - `(Recommended) 💻 Pro Developer (concise diffs, architecture patterns & CLI)`
   - `👷 Vibe Coder / Builder (intuitive visual explanations, zero terminal jargon)`
2. **"What would you like to do first?"**
   - **Option 1 (Smart Context-Aware):**
     - *If workspace already has project files:* `(Recommended) 🔍 Scan my project & install the best official Google Agent Skills`
     - *If blank chat / no project folder open:* `(Recommended) 🚀 Build & ship a new idea on Google Cloud (Gemini + Cloud Run)`
   - `🎓 Show me what's new in Antigravity (/swarm, /btw, /teamwork, MCP Apps)`
   - `📡 Show me the latest Google AI launches (g.dev/ai/googleaitech)`
   - *(Desktop / CLI / IDE ONLY — NEVER show on Antigravity Web `antigravity.google.com`):* `🎟️ I'm at an event / workshop — activate my $5 Google Cloud credit`
   - `🏆 Generate my Antigravity Builder Card for LinkedIn`

## 6. "Build & Ship a New Idea on Google Cloud" Guided Flow
When a user picks **🚀 Build & ship a new idea on Google Cloud** (or describes a fresh app idea in a blank chat), guide them smoothly through 4 short checkpoints:
1. **Clarify & Architecture:** Restate their idea in 3–4 crisp bullets, ask up to 3 clarifying questions if ambiguous, and choose the simplest right build type:
   - **Web App / API** (screens, forms, Firestore)
   - **Web App + Gemini** (Dual-Mode `google-genai` SDK — Flash default)
   - **Agentic App (ADK)** (only when multi-step tool use / autonomous planning is needed)
2. **Lazy-Load Skills & Build Locally:** Install/load only the matching official Google skills for that stack, scaffold clean code + `Dockerfile`, and verify it runs locally.
3. **Ship Live to Cloud Run:** Load `cloud-run-basics`, deploy with `--min-instances=0` (scale-to-zero!), verify the live public `https://...run.app` URL, and generate a clean `infra/teardown.sh` cleanup script.
4. **Celebrate:** Offer to generate their **LinkedIn Builder Card** featuring their newly shipped app!

## 7. On-Demand Event Credit Bridge (Desktop Only)
- If the user picks `🎟️ Activate my $5 Google Cloud credit`, asks for help claiming event credits, or pastes a credit link (`https://g.dev/credits/...` or `https://me.developers.google.com/...`):
  - **On Desktop / CLI / IDE:** Run `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --event-credit ["<CREDIT_URL>"]` to seamlessly launch the 4-step credit wizard right inside the same conversation (1 step at a time!).
  - **On Antigravity Web (`antigravity.google.com`):** Politely explain that `$5` Google Cloud / Agent Platform credits require **Antigravity Desktop or CLI** (`https://antigravity.google/download`) since Web only supports personal Google AI Pro/Ultra plans.

## 8. Live Educator & Google AI Tech Radar (Auto-Synced Daily)
Lightweight (<4 KB) auto-synced feeds work on Desktop, Web, and Cross-IDE:
- Antigravity Changelog JSON: `https://raw.githubusercontent.com/gdgworkshop/skills/main/references/antigravity_changelog.json`
- Latest Google AI Tech (`g.dev/ai/googleaitech`) JSON: `https://raw.githubusercontent.com/gdgworkshop/skills/main/references/google_ai_updates.json`
- Curated Power-Feature Educator Catalog: `https://raw.githubusercontent.com/gdgworkshop/skills/main/references/educator_catalog.json`

## 9. CLI Commands (Antigravity Desktop / Terminal)
- Detect environment + scan workspace: `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --init`
- Scan & auto-install missing official skills: `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --scan --install`
- Show latest Antigravity releases + `g.dev/ai/googleaitech` highlights + Mastery score: `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --whats-new`
- Get a smart contextual or non-repeating Educator tip: `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --tip [--context refactor|side_question|brainstorm|long_thread|debug|frontend]`
- Record feature adoption (logs Mastery + GA4 telemetry): `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --unlock <swarm|btw|teamwork|grill_me|compact|boost|browser>`
- Generate LinkedIn Builder Card (with optional `--event "DevFest Singapore 2026"`): `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --card --name "<Name>" --project "<Project>" [--event "<Event>"]`
- Direct Web Card Studio: `https://gdgworkshop.github.io/skills/card.html?name=<Name>&project=<Project>&event=<Event>&persona=<developer|builder|workshop>&features=swarm,btw,grill_me&skills=gemini-api,firebase-basics,cloud-run-basics`
- Save persona: `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --persona <developer|builder>`
- Install a specific skill or track (`ai`, `backend`, `cloud`, `mobile`, `android`): `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --install-skill <name_or_track>`
