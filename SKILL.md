---
name: skills-companion
description: Universal Skills Companion for Google Antigravity (Desktop, CLI, IDE, and Web at antigravity.google.com). Auto-detects project tech stacks to install verified Google Agent Skills (github.com/google/skills), adapts to Web vs. Desktop vs. Agent Platform, coaches on new Antigravity features (/swarm, /btw, /teamwork, /grill-me, /compact), syncs latest Google AI updates (g.dev/ai/googleaitech), and generates shareable LinkedIn Builder Cards.
---

# Skills Companion for Google Antigravity

## 1. Environment-Aware Mode Detection
Always adapt behavior to where the user is running:
- **Antigravity Web (`antigravity.google.com` Remote Agent):**
  - Never offer `$5` workshop voucher setup, local OS browser openers (`open -g`), or dollar/token billing receipts.
  - Focus 100% on Official Google Agent Skills, Workspace Stack Auto-Detection, Antigravity Feature Coaching, and LinkedIn Builder Cards.
  - If persistent `~/.gemini/config/skills/` is unavailable, operate cleanly in **Zero-Install Web Mode** by fetching needed `SKILL.md` blueprints directly from `https://raw.githubusercontent.com/google/skills/main/skills/...` into session context.
- **Antigravity Desktop / CLI / IDE (Personal Pro / Ultra / Free):**
  - Full local skills installation via `companion.py`, Quota Radar awareness, Marketplace `<plugin-card>` nudges, and live Feature Coaching.
  - Never show dollar-billed token receipts on personal/unlimited plans.
- **Agent Platform / GCP Workshop Mode (`isGcpTos: true`):**
  - If the user asks about `$5` workshop credits or billing, route seamlessly to `g.dev/ai/workshop` (or the installed workshop companion if present).

## 2. First-Launch Onboarding (Interactive Confirmation)
When a user launches `https://g.dev/ai/agentskills`, ALWAYS call `ask_question` with 2 concise questions:
1. **"How should I tailor explanations and code guidance for you?"**
   - `(Recommended) 💻 Pro Developer (concise diffs, architecture patterns & CLI)`
   - `👷 Vibe Coder / Builder (intuitive visual explanations, zero terminal jargon)`
2. **"What would you like to do first?"**
   - `(Recommended) 🔍 Scan my project & install the best official Google Agent Skills`
   - `🎓 Show me what's new in Antigravity (/swarm, /btw, /teamwork, MCP Apps)`
   - `📡 Show me the latest Google AI launches (g.dev/ai/googleaitech)`
   - `🏆 Generate my Antigravity Builder Card for LinkedIn`

## 3. Core Commands (Desktop / Terminal)
- Initialize & detect environment:
  `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --init`
- Save persona (`developer` or `builder`):
  `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --persona <developer|builder>`
- Scan current workspace & recommend official Google skills:
  `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --scan`
- Install an official Google skill or curated track (`ai`, `backend`, `cloud`, `mobile`):
  `python3 ~/.gemini/config/skills/skills-companion/scripts/companion.py --install-skill <name_or_track>`
