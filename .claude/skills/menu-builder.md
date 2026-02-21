# MenuVision - Restaurant Menu Builder (OpenClaw Skill)

Build a beautiful, self-contained HTML photo menu for any restaurant from URLs, PDFs, or photos. See the food before you order — ideal for discovering unfamiliar cuisines.

## When to Use

When the user wants to create a digital menu for a restaurant. Triggers: "build a menu", "create restaurant menu", "menu from PDF", "menu from photos", "digital menu", "openclaw", "menuvision".

## Input Sources (auto-detected)

The pipeline accepts ANY of these:
- **URL** - Restaurant website with menu (static HTML or JS-rendered)
- **PDF file** - Menu PDF (single or multi-page)
- **Image file** - Photo of a physical menu (JPG, PNG, etc.)

## Quick Start

### Quick mode (placeholders, no image gen):
```bash
python openclaw.py quick https://www.shoyu.at/menus --name "Shoyu" --tagline "Japanese Kitchen · Vienna"
```

### Fast mode (Flux.1 Schnell — $0.003/img, ~2s):
```bash
export FAL_KEY="your-key"
python openclaw.py https://www.shoyu.at/menus --name "Shoyu" --tagline "Japanese Kitchen · Vienna" --fast
```

### Quality mode (Gemini 2.5 Flash Image — $0.039/img, ~6s):
```bash
python openclaw.py https://www.shoyu.at/menus --name "Shoyu" --tagline "Japanese Kitchen · Vienna"
```

### Step by step:
```bash
python openclaw.py extract https://www.shoyu.at/menus          # → menu_data_shoyu.json
python openclaw.py images menu_data_shoyu.json --fast           # → images/shoyu/*.jpg
python openclaw.py build menu_data_shoyu.json --name "Shoyu"    # → Shoyu_Menu.html
```

## Pipeline Architecture

```
Source (URL/PDF/Photo)
    │
    ▼
┌─────────────┐     Gemini 2.5 Flash
│ extract_menu │────► Vision/Text extraction
│   .py       │     JSON mode, 65k output tokens
└──────┬──────┘
       │ menu_data.json
       ▼
┌──────────────┐    Gemini 2.5 Flash Image ($0.039/img, ~6s)
│ generate_    │    OR Flux.1 Schnell ($0.003/img, ~2s)
│ images.py    │
└──────┬───────┘
       │ images/*.jpg (800x800)
       ▼
┌─────────────┐
│ build_menu  │────► Restaurant_Menu.html
│   .py       │     Self-contained, Instagram-style
└─────────────┘
```

## File Reference

| File | Purpose |
|------|---------|
| `openclaw.py` | CLI orchestrator (full/quick/step-by-step) |
| `extract_menu.py` | Unified extractor: URL/PDF/photo → JSON |
| `generate_images.py` | Food image generator (Gemini or Flux.1) |
| `build_menu.py` | Parameterized HTML builder |

## Extraction Details

### HTML URLs
1. Fetches page with `requests`
2. Checks text density to detect static vs JS-rendered
3. **Static** (density >= 0.02): Cleans HTML, sends text to Gemini 2.5 Flash (JSON mode)
4. **JS-rendered** (Wix, Framer, etc.): Screenshots with Playwright, sends to Gemini Vision
5. **Large menus** (>12k chars): Chunked extraction, merged like PDF multi-page

### PDF Files
1. Converts each page to image via PyMuPDF (200 DPI)
2. Sends each page image to Gemini Vision
3. Merges results across pages

### Photos
1. Loads image directly
2. Sends to Gemini Vision (resizes if >10MB)

## Image Generation

### Shared Prompt Style
Casual phone photo aesthetic — "someone quickly snapped a photo before eating":
- Plate takes ~30% of frame (NOT a close-up)
- Dark wooden table, chopsticks/cutlery/glasses scattered naturally
- Blurred restaurant interior background
- Warm ambient lighting, natural depth of field

### Quality Mode (default) - Gemini 2.5 Flash Image
- $0.039/image, ~6s sequential
- Best image quality, most realistic

### Fast Mode - Flux.1 Schnell via fal.ai
- $0.003/image (13x cheaper), ~2s parallel
- Good quality, slightly less realistic
- Requires FAL_KEY env var

## HTML Output Features
- 3-column Instagram-style grid (9:16 portrait tiles)
- Gradient text overlay with name + secondary language + price
- Tap-to-select with green checkmark
- Receipt/bill on Selection tab with +/- quantity controls
- Category pill navigation with scroll sync
- Drinks section below grid with currency-prefixed prices
- Allergen legend
- Fully responsive, dark mode
- Self-contained (all CSS/JS inline, only Google Fonts external)

## Branding Customization
```bash
--name "Restaurant Name"     # Header brand text
--tagline "Cuisine · City"   # Subtitle
--accent "#ff6b00"           # Primary color (pills, active tab, drink prices)
--bg "#0a0a0a"               # Background color
```

## Cost Summary

| Component | Quality Mode | Fast Mode |
|-----------|-------------|-----------|
| Extraction (per page) | ~$0.001 | ~$0.001 |
| Images (per item) | $0.039 | $0.003 |
| **80-item restaurant** | **~$3.12** | **~$0.24** |
| Time (80 items) | ~8 min | ~90s (5 workers) |

## Dependencies

Required:
- `google-genai` (extraction + quality images)
- `Pillow` (image processing)

For HTML URLs:
- `requests` (HTTP fetching)
- `beautifulsoup4` (HTML parsing)

For JS-rendered sites:
- `playwright` (headless browser screenshots)

For PDF files:
- `PyMuPDF` (PDF to image conversion)

For fast image mode:
- `fal-client` (Flux.1 Schnell API)

Install all:
```bash
pip install google-genai Pillow requests beautifulsoup4 PyMuPDF
pip install playwright && playwright install chromium
pip install fal-client  # optional, for --fast mode
```

## Environment Variables
- `GOOGLE_API_KEY` - Required for extraction and quality image gen
- `FAL_KEY` - Required for fast image gen (Flux.1 Schnell)
- `XAI_API_KEY` - Required for Grok image gen
- `GITHUB_PAT` - Required for GitHub Pages publishing
- `GITHUB_OWNER` - Your GitHub username (default: reads from git config)
- `GITHUB_REPO` - Your GitHub Pages repo name (default: `menus`)

## Publishing to GitHub Pages

### Setup (one-time)
1. Create a GitHub repo for your menus (e.g. `your-username/menus`)
2. Enable GitHub Pages on the `main` branch
3. Set environment variables:
```bash
export GITHUB_PAT="your-personal-access-token"
export GITHUB_OWNER="your-username"    # optional if git config is set
export GITHUB_REPO="menus"             # optional, defaults to "menus"
```

### Publish a menu
```bash
python publish_menu.py Restaurant_Menu.html --name "Restaurant" --tagline "Cuisine · City" --cuisine Type
```

Your gallery: `https://<your-username>.github.io/<repo>/`
Individual menus: `https://<your-username>.github.io/<repo>/Restaurant_Menu.html`

## Serving (local preview)
```bash
python -m http.server 8080 --bind 0.0.0.0
# Access at http://localhost:8080/Restaurant_Menu.html
```

## Test Cases Validated (12 restaurants)

| Restaurant | Source | Items | Status |
|-----------|--------|-------|--------|
| Shoyu (E2E with images) | URL | 91 | PASS |
| Feuervogel | URL | 28 | PASS |
| Origami Sushi | URL | 234 | PASS |
| Namaste Wien | URL | 74 | PASS |
| Indian Cuisine | URL | 135 | PASS |
| Spice of India | URL | 79 | PASS |
| In-Dish (Framer) | URL | 51 | PASS |
| An's Kitchen | URL | 55 | PASS |
| Weinpresse | URL | 5 | PASS |
| Business Lunch | PDF | 25 | PASS |
| Hauptmenu | PDF | 118 | PASS |
| Jaritas (Wix tabs) | URL | 5/~50 | PARTIAL |

## Known Limitations
- Tabbed Wix menus: Only first visible tab extracted
- Google Maps photo URLs: Not supported (use direct image files)
- Very large menus (300+ items): May need manual chunk review
