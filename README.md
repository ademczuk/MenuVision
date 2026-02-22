# MenuVision

Build beautiful, self-contained HTML photo menus for any restaurant from URLs, PDFs, or photos. Works with menus in any language.

## What is this?

MenuVision is an **OpenClaw / Claude Code skill** — a build specification that AI coding assistants use to create restaurant menus end-to-end. The skill file contains the full data contract, extraction prompts, and pipeline architecture so the AI agent can generate working code from scratch.

1. **Extract** menu data from a website URL, PDF, or photo → structured JSON (Gemini Vision)
2. **Generate** food photos using AI (Gemini Image)
3. **Build** a self-contained HTML menu with Instagram-style grid, tap-to-select, receipt view, and currency converter

## How to Use

### Method 1: Claude Code (automatic — recommended)

```bash
git clone https://github.com/ademczuk/MenuVision.git
cd MenuVision
cp .env.example .env   # fill in your API keys
```

Open the project in Claude Code. The skill is auto-discovered from `.claude/skills/`. Just ask:

- "Build a menu for https://www.shoyu.at/menus"
- "Create a photo menu from this PDF" (attach file)
- "Make a digital menu from these photos"

### Method 2: Any AI coding assistant

Copy `.claude/skills/menu-builder.md` into your project and reference it in your prompt. The file contains everything the AI needs: JSON schema, extraction prompt, image prompt template, API config, and multilingual handling.

### Method 3: OpenClaw messaging bot (Telegram, WhatsApp, Discord, etc.)

Deploy the skill to your OpenClaw gateway container:

```bash
cp .claude/skills/menu-builder.md /path/to/openclaw/workspace/skills/menuvision/SKILL.md
```

The skill activates on triggers: "menu", "menuvision", "restaurant", "build menu", "photo menu". Works with any messaging platform supported by your OpenClaw gateway.

## What's in the Skill File

The core of this repo is [`.claude/skills/menu-builder.md`](.claude/skills/menu-builder.md) — a complete build specification containing:

- **JSON data contract** — the exact schema all pipeline stages share (breaks if deviated from)
- **Extraction prompt** — 12-rule Gemini prompt that defines schema + extraction behavior
- **Gemini API config** — model name, JSON mode, 64K token limit, truncation detection
- **Image prompt template** — `build_food_prompt()` for casual phone-photo aesthetic
- **Multilingual/CJK handling** — bilingual fields, Unicode detection, Latin-script prompt routing
- **File naming conventions** — `images/{stem}/{code}.jpg` pattern + case-insensitive fallback
- **HTML output spec** — responsive grid, selection system, allergen legend, branding
- **Cost breakdown** — per-image and per-menu pricing

## Environment Variables

| Variable | Required For |
|----------|-------------|
| `GOOGLE_API_KEY` | Menu extraction + image generation (Gemini) |
| `GITHUB_PAT` | Publishing to GitHub Pages |
| `GITHUB_OWNER` | Your GitHub username |
| `GITHUB_REPO` | Your GitHub Pages repo (default: `menus`) |

## Cost

| Component | Cost |
|-----------|------|
| Per image (Gemini) | $0.039 |
| 80-item menu | ~$3.12 |
| Time (80 items) | ~8 min |

## License

MIT
