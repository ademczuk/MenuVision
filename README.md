# MenuVision

Build beautiful, self-contained HTML photo menus for any restaurant from URLs, PDFs, or photos. See the food before you order.

## What is this?

MenuVision is an **OpenClaw skill** — a structured prompt that AI coding assistants (Claude Code, etc.) can use to build restaurant menus end-to-end. The skill file describes the full pipeline:

1. **Extract** menu data from a website URL, PDF, or photo using Gemini Vision
2. **Generate** food photos using AI (Gemini Image or Flux.1 Schnell)
3. **Build** a self-contained HTML menu with Instagram-style grid, tap-to-select, and receipt view

## Quick Start

1. Clone this repo
2. Copy `.env.example` to `.env` and fill in your API keys
3. Point your AI coding assistant at `.claude/skills/menu-builder.md`
4. Ask it to build a menu for any restaurant

## Skill File

The core of this repo is [`.claude/skills/menu-builder.md`](.claude/skills/menu-builder.md) — a comprehensive guide covering:

- Pipeline architecture (extract → generate images → build HTML)
- Multiple image generation backends with cost comparison
- HTML output features (responsive grid, selection system, allergen legend)
- Branding customization options
- GitHub Pages publishing setup

## Environment Variables

| Variable | Required For |
|----------|-------------|
| `GOOGLE_API_KEY` | Menu extraction + quality image gen (Gemini) |
| `FAL_KEY` | Fast image gen (Flux.1 Schnell via fal.ai) |
| `XAI_API_KEY` | Grok image gen (xAI) |
| `GITHUB_PAT` | Publishing to GitHub Pages |
| `GITHUB_OWNER` | Your GitHub username |
| `GITHUB_REPO` | Your GitHub Pages repo (default: `menus`) |

## Cost

| Mode | Per Image | 80-item Menu | Speed |
|------|-----------|-------------|-------|
| Quality (Gemini) | $0.039 | ~$3.12 | ~8 min |
| Fast (Flux.1) | $0.003 | ~$0.24 | ~90s |

## License

MIT
