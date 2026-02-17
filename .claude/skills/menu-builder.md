# Restaurant Menu Builder

Build a beautiful, self-contained HTML photo menu for any restaurant from PDF pages or photos of a physical menu.

## When to Use

When the user wants to create a digital menu for a restaurant. Triggers: "build a menu", "create restaurant menu", "menu from PDF", "menu from photos", "digital menu".

## Input Requirements

Ask the user for:
1. **Menu source** - PDF file(s) or photos of each menu page
2. **Restaurant name** - e.g. "TanTan Chinese Fine Dining"
3. **Tagline** - e.g. "Chinese Fine Dining · Vienna"
4. **Cuisine type** - Chinese, Italian, Japanese, etc.
5. **Brand colors** (optional) - primary accent color (default: `#c41e3a`), background (default: `#0a0a0a`)
6. **Logo file** (optional)
7. **Languages** - primary + secondary (e.g. German + English, or English + Chinese)
8. **Image generation mode** - "quality" (default, Gemini Image ~$0.039/image) or "fast" (Flux.1 Schnell ~$0.003/image)

## Pipeline Overview

### Step 1: Extract Menu Data (Vision AI)

Use vision AI to read each menu page and extract structured JSON:

```python
# --- OPTION A: Gemini 1.5 Flash (CHEAP - $0.0004/page) ---
# Best for: most menus, clear layouts
from google import genai

client = genai.Client(api_key=GEMINI_API_KEY)

def extract_menu_page(image_path: str) -> dict:
    """Extract menu items from a single page image using Gemini Flash."""
    import base64
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            {
                "parts": [
                    {"text": EXTRACTION_PROMPT},
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
                ]
            }
        ]
    )
    return json.loads(response.text)

EXTRACTION_PROMPT = """Analyze this restaurant menu page. Extract ALL items into this JSON structure:
{
  "sections": [
    {
      "title": "Section Name",
      "title_secondary": "Section name in other language if present",
      "note": "Any section note (e.g. 'served with rice')",
      "items": [
        {
          "code": "M1",
          "name": "Dish Name",
          "name_secondary": "Name in other language",
          "description": "Brief description",
          "description_secondary": "Description in other language",
          "allergens": "A C F",
          "price": "12,90",
          "dietary": ["vegan", "spicy"]
        }
      ]
    }
  ]
}
Rules:
- Extract EVERY item, do not skip any
- Preserve original item codes/numbers if present
- Extract prices exactly as written (with comma for European format)
- Note allergen codes if present
- Identify dietary flags: vegan, vegetarian, spicy, gluten-free
- If bilingual, capture both languages
- For sections with no explicit title, infer from context (e.g. "Starters", "Mains")
Return ONLY valid JSON, no markdown fences."""


# --- OPTION B: Claude Sonnet (ACCURATE - $0.015/page) ---
# Best for: complex layouts, handwritten menus, unusual formatting
import anthropic

def extract_menu_page_claude(image_path: str) -> dict:
    """Extract menu items using Claude Sonnet for complex layouts."""
    import base64
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
                {"type": "text", "text": EXTRACTION_PROMPT}
            ]
        }]
    )
    return json.loads(response.content[0].text)
```

**Strategy**: Try Gemini Flash first. If the extracted data looks incomplete or garbled (< 50% of expected items, malformed JSON), fall back to Claude Sonnet for that page.

### Step 2: User Review

Present extracted data to the user for verification. Show each section with items, prices, and translations. Let them correct any OCR mistakes before proceeding.

### Step 3: Enhance Data

Fill in missing fields:
- Generate English/German translations if menu is single-language
- Add brief descriptions for items that lack them
- Infer dietary flags (vegan, spicy) from ingredients
- Generate item codes if the menu doesn't have them (e.g. M1, K1, H1...)

### Step 4: Generate Food Images

#### QUALITY MODE (Default) - Gemini 2.5 Flash Image

~$0.039/image, ~4s/image, high quality food photos.

```python
from google import genai
import io
from pathlib import Path
from PIL import Image

COST_PER_IMAGE = 0.039

def build_food_prompt(name: str, description: str) -> str:
    return (
        f"Generate an image: {name} - {description}. "
        "Wide shot showing the ENTIRE plate centered on a dark wooden table, "
        "photographed from a 45-degree angle sitting across the table. "
        "The plate takes up about 40% of the frame. "
        "Visible table surface, chopsticks, other dishes slightly visible at edges. "
        "Blurred restaurant background with warm ambient lighting. "
        "Casual phone photo, natural depth of field, authentic restaurant atmosphere. "
        "Do NOT zoom in close to the food. Show the full scene."
    )

def generate_food_image(client, name: str, description: str, output_path: Path):
    prompt = build_food_prompt(name, description)
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            img = Image.open(io.BytesIO(part.inline_data.data)).convert("RGB")
            # Center-crop to square, resize to 800x800
            w, h = img.size
            side = min(w, h)
            left = (w - side) // 2
            top = (h - side) // 2
            img = img.crop((left, top, left + side, top + side))
            img = img.resize((800, 800), Image.LANCZOS)
            img.save(str(output_path), "JPEG", quality=82)
            return
    raise RuntimeError("No image in response")
```

#### FAST MODE - Flux.1 Schnell via fal.ai

~$0.003/image (13x cheaper), ~2s/image, good quality.

```python
import fal_client
import requests
from pathlib import Path
from PIL import Image
import io

COST_PER_IMAGE = 0.003

def generate_food_image_fast(name: str, description: str, output_path: Path):
    """Generate food image using Flux.1 Schnell via fal.ai."""
    prompt = (
        f"Professional food photography: {name} - {description}. "
        "Wide shot, entire plate centered on dark wooden table, "
        "45-degree angle, plate takes 40% of frame, "
        "chopsticks and table visible, warm restaurant lighting, "
        "natural phone photo look, shallow depth of field."
    )

    result = fal_client.subscribe(
        "fal-ai/flux/schnell",
        arguments={
            "prompt": prompt,
            "image_size": {"width": 1024, "height": 1024},
            "num_inference_steps": 4,
            "num_images": 1,
        },
    )

    image_url = result["images"][0]["url"]
    response = requests.get(image_url)
    img = Image.open(io.BytesIO(response.content)).convert("RGB")
    img = img.resize((800, 800), Image.LANCZOS)
    img.save(str(output_path), "JPEG", quality=82)


# Progressive generation with parallel workers
import concurrent.futures

def generate_all_images(items: list, output_dir: Path, max_workers: int = 5):
    """Generate all food images with parallel workers for speed."""
    output_dir.mkdir(parents=True, exist_ok=True)

    def gen_one(item):
        code, name, desc = item["code"], item["name"], item.get("description", item["name"])
        path = output_dir / f"{code}.jpg"
        if path.exists():
            return code, "skipped"
        try:
            generate_food_image_fast(name, desc, path)
            return code, "ok"
        except Exception as e:
            return code, f"failed: {e}"

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(gen_one, item): item for item in items}
        for future in concurrent.futures.as_completed(futures):
            code, status = future.result()
            print(f"  {code}: {status}")
```

### Step 5: Build Self-Contained HTML

Generate the final HTML file with all CSS/JS inline and images referenced relatively.

#### Key Architecture

```python
import html as html_mod
import base64
from pathlib import Path

def build_menu_html(
    restaurant_name: str,
    tagline: str,
    accent_color: str,       # e.g. "#c41e3a"
    bg_color: str,            # e.g. "#0a0a0a"
    food_sections: list,      # [{title, chinese, items: [{code, name, chinese, price, ...}]}]
    drink_sections: list,     # [{title, chinese, items: [(name, price, detail)]}]
    images_dir: str,          # relative path to images folder
    allergen_map: dict,       # {code: description}
) -> str:
    """Build complete self-contained HTML menu."""
    # ... (see build_tantan_menu.py for full implementation)
```

#### HTML Structure

```
<header class="site-header">        ← Sticky floating header
  <div class="header-brand">         ← Restaurant name
  <div class="header-tagline">       ← Tagline
  <div class="tab-bar">              ← Menu | Selection tabs
    <button class="tab" data-tab="menu">Menu</button>
    <button class="tab" data-tab="selection">Selection <badge/></button>
  </div>
  <div class="cat-nav">              ← Scrollable category pills
    <button class="cat-pill" data-cat="all">All</button>
    <button class="cat-pill" data-cat="starters">Starters</button>
    ...
  </div>
</header>

<div id="tab-menu" class="tab-content active">
  <div class="menu-grid">            ← 3-column Instagram grid (9:16 tiles)
    <div class="menu-tile" data-code="M1" onclick="toggleSelect(this)">
      <div class="tile-image"><img .../></div>
      <div class="tile-check">...</div>  ← Green checkmark (hidden until selected)
      <div class="tile-caption">          ← Gradient overlay with name + price
        <span class="tile-name">...</span>
        <span class="tile-chinese">...</span>
        <span class="tile-price">...</span>
      </div>
    </div>
    ...
  </div>
  <div class="container">             ← Drinks + allergens below grid
    ... drink sections with selectable rows ...
    ... allergen legend ...
  </div>
</div>

<div id="tab-selection" class="tab-content">
  <div class="receipt">               ← Dark-mode receipt/bill
    ... dynamically built from selections ...
    ... +/- quantity controls per item ...
    ... running total ...
    ... Clear All button ...
  </div>
</div>
```

#### CSS Grid System

```css
/* 3-column Instagram-style grid */
.menu-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 3px;
}
.menu-tile {
  position: relative;
  overflow: hidden;
  aspect-ratio: 9 / 16;
  cursor: pointer;
}
/* Gradient text overlay */
.menu-tile::after {
  content: '';
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 45%;
  background: linear-gradient(transparent, rgba(0,0,0,0.7));
  pointer-events: none;
}
```

#### Selection JavaScript

```javascript
const selected = new Map(); // code -> {name, price, chinese, qty}

function toggleSelect(el) {
  const code = el.dataset.code;
  if (selected.has(code)) {
    selected.delete(code);
    el.classList.remove('selected');
  } else {
    selected.set(code, {
      name: el.dataset.name,
      price: el.dataset.price,
      chinese: el.querySelector('.tile-chinese')?.textContent || '',
      qty: 1
    });
    el.classList.add('selected');
  }
  updateReceipt();
}

function changeQty(code, delta) {
  const item = selected.get(code);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) {
    selected.delete(code);
    document.querySelectorAll('[data-code="' + code + '"]').forEach(el => el.classList.remove('selected'));
  }
  updateReceipt();
}

function clearAll() {
  selected.clear();
  document.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
  updateReceipt();
}
```

## Cost Summary

| Component | Quality Mode | Fast Mode |
|-----------|-------------|-----------|
| Menu extraction (per page) | $0.0004 (Gemini Flash) | $0.0004 (Gemini Flash) |
| Image generation (per item) | $0.039 (Gemini Image) | $0.003 (Flux.1 Schnell) |
| **75-item restaurant** | **~$2.93** | **~$0.23** |
| Time (75 items) | ~5 min sequential | ~30s with 5 parallel workers |

## Branding Customization

The template uses CSS custom properties for easy theming:

```css
:root {
  --accent: #c41e3a;      /* Restaurant's primary color */
  --bg: #0a0a0a;          /* Background */
  --text: #e0d8d0;        /* Body text */
  --card-bg: #141414;     /* Card/section backgrounds */
}
```

## Reference Implementation

The complete working implementation is in:
- `C:\Projects\TanTan_Menu_Package\build_tantan_menu.py` - Full build script (HTML generation, all CSS/JS, menu data structure)
- `C:\Projects\TanTan_Menu_Package\generate_nanobananav2.py` - Gemini Image generator (quality mode)

## Quick Start

To build a menu for a new restaurant:

1. Collect menu pages (PDF or photos)
2. Run extraction on each page → get structured JSON
3. Present to user for review/correction
4. Generate food images (quality or fast mode)
5. Populate the HTML template with restaurant branding + extracted data
6. Output: single `Restaurant_Menu.html` + `images/` folder
7. Serve locally: `python -m http.server 8080`
