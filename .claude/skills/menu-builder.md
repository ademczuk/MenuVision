---
name: menuvision
description: "Build beautiful HTML photo menus from restaurant URLs, PDFs, or photos using Gemini Vision and AI image generation"
emoji: "🍽️"
user-invocable: true
metadata: {"openclaw": {"version": "1.0.0", "triggers": ["menu", "menuvision", "restaurant", "build menu", "photo menu", "digital menu", "menu from PDF", "menu from photos"], "requires": {"bins": ["python3"]}}}
---

# MenuVision - Restaurant Menu Builder

Build a self-contained HTML photo menu for any restaurant from URLs, PDFs, or photos.

## When to Use

When the user wants to create a digital menu for a restaurant. Triggers: "build a menu", "create restaurant menu", "menu from PDF", "menu from photos", "digital menu", "menuvision".

## Quick Start

```
1. Extract:  URL/PDF/photo  →  menu_data.json     (Gemini Vision)
2. Generate: menu_data.json →  images/*.jpg        (Gemini Image or Flux.1)
3. Build:    menu_data.json + images → Menu.html   (self-contained HTML)
```

### Example usage (ask the AI):
- "Build a menu for https://www.shoyu.at/menus"
- "Create a photo menu from this PDF" (attach file)
- "Make a digital menu from these photos of a restaurant menu"

## Pipeline Components

The AI agent creates these scripts:

| Script | Purpose |
|--------|---------|
| `extract_menu.py` | Extract menu data from URL/PDF/photo → structured JSON |
| `generate_images.py` | Generate food photos via Gemini Image or Flux.1 Schnell |
| `build_menu.py` | Build self-contained HTML menu from JSON + images |
| `publish_menu.py` | (Optional) Publish HTML to GitHub Pages |

---

## DATA CONTRACT (Critical)

All three pipeline stages share this exact JSON schema. The AI agent MUST use these field names — any deviation breaks the pipeline.

### menu_data.json Schema

```json
{
  "restaurant": {
    "name": "Restaurant Name (if visible)",
    "cuisine": "cuisine type (Chinese, Indian, Austrian, Japanese, etc.)",
    "tagline": "any subtitle or tagline"
  },
  "sections": [
    {
      "title": "Section Name (in primary language)",
      "title_secondary": "Section name in secondary language (if present, else empty string)",
      "category": "food or drink",
      "note": "Any section note (e.g. 'served with rice', 'Mon-Fri 11-15h')",
      "items": [
        {
          "code": "M1",
          "name": "Dish Name (primary language)",
          "name_secondary": "Name in secondary language (if present)",
          "description": "Brief description (primary language)",
          "description_secondary": "Description in secondary language (if present)",
          "price": "12,90",
          "price_prefix": "",
          "allergens": "A C F",
          "dietary": ["vegan", "spicy"],
          "variants": []
        }
      ]
    }
  ],
  "allergen_legend": {
    "A": "Gluten",
    "B": "Crustaceans"
  },
  "metadata": {
    "languages": ["German", "English"],
    "currency": "EUR",
    "price_format": "European comma"
  }
}
```

### Field Reference

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `sections[].category` | `"food"` or `"drink"` | Yes | Drives food grid vs drink list layout |
| `items[].code` | string | Yes | Unique per item. Links to image filename. Use existing codes (M1, K2) or generate (A1, A2) |
| `items[].name` | string | Yes | Primary language. For CJK menus, this is the CJK name |
| `items[].name_secondary` | string | No | Secondary language. For CJK menus, this is the English/Latin name |
| `items[].price` | string | Yes | Preserve original format ("12,90" not "12.90") |
| `items[].price_prefix` | string | No | e.g. "ab" (starting from), "ca." |
| `items[].variants` | array | No | `[{"label": "6 Stk", "price": "8,90"}, ...]` — set main price to smallest variant |
| `items[].allergens` | string | No | Space-separated codes exactly as printed: "A C F" |
| `items[].dietary` | array | No | `["vegan", "vegetarian", "spicy", "gluten-free", "halal", "kosher"]` |
| `metadata.currency` | string | Yes | ISO code: "EUR", "USD", "JPY", "CNY", "THB", etc. |

---

## EXTRACTION PROMPT

Send this exact prompt to Gemini. It defines the schema AND the extraction rules. Do not paraphrase it.

```
You are a restaurant menu data extractor. Analyze this menu content and extract ALL items into structured JSON.

Return this exact JSON structure:
{
  "restaurant": {
    "name": "Restaurant Name (if visible)",
    "cuisine": "cuisine type (Chinese, Indian, Austrian, Japanese, etc.)",
    "tagline": "any subtitle or tagline"
  },
  "sections": [
    {
      "title": "Section Name (in primary language)",
      "title_secondary": "Section name in secondary language (if present, else empty string)",
      "category": "food or drink",
      "note": "Any section note (e.g. 'served with rice', 'Mon-Fri 11-15h')",
      "items": [
        {
          "code": "M1",
          "name": "Dish Name (primary language)",
          "name_secondary": "Name in secondary language (if present)",
          "description": "Brief description (primary language)",
          "description_secondary": "Description in secondary language (if present)",
          "price": "12,90",
          "price_prefix": "",
          "allergens": "A C F",
          "dietary": ["vegan", "spicy"],
          "variants": []
        }
      ]
    }
  ],
  "allergen_legend": {
    "A": "Gluten",
    "B": "Crustaceans"
  },
  "metadata": {
    "languages": ["German", "English"],
    "currency": "EUR",
    "price_format": "European comma"
  }
}

CRITICAL RULES:
1. Extract EVERY item. Do not skip ANY dish, drink, or menu entry.
2. Preserve original item codes/numbers if present (M1, K2, S3, etc.). If none exist, generate sequential codes per section (e.g. A1, A2 for appetizers, M1, M2 for mains).
3. Extract prices EXACTLY as written (preserve comma/period format).
4. If an item has a price prefix like "ab" (starting from), capture it in "price_prefix".
5. If an item has multiple size/quantity variants (e.g. 6 Stk / 12 Stk / 18 Stk at different prices), use the "variants" array:
   [{"label": "6 Stk", "price": "8,90"}, {"label": "12 Stk", "price": "15,90"}]
   In this case, set the main "price" to the smallest variant's price.
6. Capture allergen codes exactly as shown (letters, numbers, or symbols).
7. If an allergen legend is visible anywhere, include it in "allergen_legend".
8. Identify dietary flags from descriptions/icons: vegan, vegetarian, spicy, gluten-free, halal, kosher.
9. If the menu is bilingual, capture BOTH languages. Put the primary/dominant language in name/description and the secondary in name_secondary/description_secondary.
10. For set menus or lunch specials with a fixed price covering multiple choices, create a section with note explaining the format, and list each choice as an item.
11. Classify each section as "food" or "drink".
12. For drinks, still extract name, price, and any size variants.

Return ONLY valid JSON. No markdown fences, no explanatory text.
```

---

## GEMINI API CONFIGURATION

```python
import google.genai as genai

client = genai.Client()  # uses GOOGLE_API_KEY env var

def gemini_config():
    return genai.types.GenerateContentConfig(
        max_output_tokens=65536,          # 64K — needed for large menus
        response_mime_type="application/json",  # JSON mode — critical
    )

# Model: gemini-2.5-flash (default)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt_text,    # or [image, prompt_text] for vision
    config=gemini_config(),
)

# ALWAYS check for truncation
if response.candidates[0].finish_reason.name == "MAX_TOKENS":
    print("WARNING: Response truncated. Menu may be incomplete.")
```

---

## IMAGE PROMPT TEMPLATE

Use this exact function. It produces the casual phone-photo aesthetic that makes menus look authentic.

```python
def build_food_prompt(name: str, description: str, cuisine: str = "") -> str:
    cuisine_context = f" {cuisine}" if cuisine else ""
    food_desc = f"{name}"
    if description and description != name:
        food_desc += f" ({description})"

    return (
        f"A photo of {food_desc} at a{cuisine_context} restaurant. "
        f"Taken casually with a phone from across the table at a 45-degree angle. "
        f"The plate sits on a dark wooden table and takes up only 30% of the frame. "
        f"Lots of visible table surface around the plate. Chopsticks, napkins, "
        f"a glass of water, and small side dishes scattered naturally nearby. "
        f"Blurred restaurant interior in the background — other diners, pendant lights, "
        f"wooden chairs visible but out of focus. Warm ambient lighting. "
        f"NOT a close-up. NOT professional food photography. "
        f"It looks like someone quickly snapped a photo before eating."
    )
```

---

## MULTILINGUAL / CJK HANDLING

Menus can be in ANY language. The pipeline handles this through bilingual fields and smart prompt routing.

### Extraction (all languages)
- `name` / `description` = primary language (whatever the menu is mostly written in)
- `name_secondary` / `description_secondary` = secondary language (if bilingual)
- Works for: German/English, Chinese/English, Japanese/English, Thai/English, Arabic/English, Korean/English, etc.

### Image Generation (CJK-safe prompting)
CJK characters produce bad image prompts. Before calling `build_food_prompt()`, swap to the Latin name:

```python
def prepare_for_image_gen(name, name_secondary, description):
    """Use Latin-script name for image prompts. CJK → use secondary name."""
    display_name = name
    if name_secondary:
        if any(ord(c) > 0x2E80 for c in name):  # CJK/Hangul/Kana detection
            display_name = name_secondary
            description = description or name
        else:
            description = description or name_secondary
    return display_name, description
```

**Unicode ranges covered by `ord(c) > 0x2E80`:**
- CJK Unified Ideographs (Chinese characters)
- Hiragana / Katakana (Japanese)
- Hangul (Korean)
- CJK Compatibility, Radicals, Extensions

### HTML Output (all scripts)
- `name` renders as the large display text
- `name_secondary` renders below it in smaller text
- Both use Google Fonts with CJK fallback (`Noto Sans SC`, `Noto Sans JP`, `Noto Sans KR`)

---

## FILE NAMING CONVENTIONS

### Image files
```
images/{restaurant_stem}/{code}.jpg

# restaurant_stem = data filename minus "menu_data_" prefix
# Example: menu_data_shoyu.json → images/shoyu/M1.jpg
```

### Image path matching (in build step)
```python
def find_image(code, images_dir):
    # 1. Exact match: {code}.jpg, .jpeg, .webp, .png
    for ext in ("jpg", "jpeg", "webp", "png"):
        candidate = images_dir / f"{code}.{ext}"
        if candidate.exists():
            return candidate
    # 2. Case-insensitive fallback
    for f in images_dir.iterdir():
        if f.stem.lower() == code.lower() and f.suffix.lower() in (".jpg", ".jpeg", ".webp", ".png"):
            return f
    return None
```

### Output HTML
```
{RestaurantName}_Menu.html    # self-contained, all images base64-encoded inline
```

---

## EXTRACTION DETAILS

### HTML URLs
1. Fetch page with `requests`
2. Check text density to detect static vs JS-rendered
3. **Static** (density >= 0.02): Clean HTML, send text to Gemini 2.5 Flash (JSON mode)
4. **JS-rendered** (Wix, Framer, etc.): Screenshot with Playwright, send to Gemini Vision
5. **Large menus** (>12k chars): Chunked extraction, merge like PDF multi-page

### PDF Files
1. Convert each page to image via PyMuPDF (200 DPI)
2. Send each page image to Gemini Vision
3. Merge results across pages (deduplicate items by code)

### Photos
1. Load image directly
2. Resize if >10MB
3. Send to Gemini Vision

---

## IMAGE GENERATION

### Quality Mode (default) — Gemini 2.5 Flash Image
- `$0.039/image`, ~6s sequential
- Best quality, most realistic
- Uses `GOOGLE_API_KEY`

### Fast Mode — Flux.1 Schnell via fal.ai
- `$0.003/image` (13x cheaper), ~2s parallel (5 workers)
- Good quality, slightly less realistic
- Uses `FAL_KEY`

---

## HTML OUTPUT FEATURES
- 3-column Instagram-style grid (9:16 portrait tiles)
- Gradient text overlay with name + secondary language + price
- Tap-to-select with green checkmark
- Receipt/bill on Selection tab with +/- quantity controls
- Category pill navigation with scroll sync
- Drinks section below grid with currency-prefixed prices
- Allergen legend
- Fully responsive, dark mode
- Self-contained (all CSS/JS inline, images base64, only Google Fonts external)

## Branding Customization
```bash
--name "Restaurant Name"     # Header brand text
--tagline "Cuisine · City"   # Subtitle
--accent "#ff6b00"           # Primary color (pills, active tab, drink prices)
--bg "#0a0a0a"               # Background color
```

---

## COST SUMMARY

| Component | Quality Mode | Fast Mode |
|-----------|-------------|-----------|
| Extraction (per page) | ~$0.001 | ~$0.001 |
| Images (per item) | $0.039 | $0.003 |
| **80-item restaurant** | **~$3.12** | **~$0.24** |
| Time (80 items) | ~8 min | ~90s (5 workers) |

## DEPENDENCIES

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

```bash
pip install google-genai Pillow requests beautifulsoup4 PyMuPDF
pip install playwright && playwright install chromium
pip install fal-client  # optional, for --fast mode
```

## ENVIRONMENT VARIABLES
- `GOOGLE_API_KEY` — Required for extraction and quality image gen
- `FAL_KEY` — Required for fast image gen (Flux.1 Schnell)
- `GITHUB_PAT` — Required for GitHub Pages publishing
- `GITHUB_OWNER` — Your GitHub username (default: reads from git config)
- `GITHUB_REPO` — Your GitHub Pages repo name (default: `menus`)

## PUBLISHING TO GITHUB PAGES

### Setup (one-time)
1. Create a GitHub repo for your menus (e.g. `your-username/menus`)
2. Enable GitHub Pages on the `main` branch
3. Set environment variables:
```bash
export GITHUB_PAT="your-personal-access-token"
export GITHUB_OWNER="your-username"
export GITHUB_REPO="menus"
```

### Publish
```bash
python publish_menu.py Restaurant_Menu.html --name "Restaurant" --tagline "Cuisine · City" --cuisine Type
```

Gallery: `https://<your-username>.github.io/<repo>/`

## KNOWN LIMITATIONS
- Tabbed Wix menus: Only first visible tab extracted
- Google Maps photo URLs: Not supported (use direct image files)
- Very large menus (300+ items): May need manual chunk review
