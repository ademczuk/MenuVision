#!/usr/bin/env python3
"""
generate_grok.py - Generate food images for TanTan Chinese Restaurant Menu
Uses xAI Grok Image API to produce natural-looking food photos.

Pricing:
    grok-imagine-image     $0.02/image  (300 RPM)
    grok-2-image-1212      $0.07/image  (300 RPM) - better quality
    grok-imagine-image-pro $0.07/image  (30 RPM)

Usage:
    python generate_grok.py --api-key YOUR_KEY
    python generate_grok.py --dry-run
    python generate_grok.py --items M1 K1 H4 --force
    python generate_grok.py --model grok-imagine-image   # cheaper
"""

import argparse
import io
import os
import sys
import time
import json
import requests
from pathlib import Path

# ---------------------------------------------------------------------------
# Menu item definitions -- all 75 items (same as nanobananav2)
# ---------------------------------------------------------------------------

MENU_ITEMS = [
    # LUNCH (M1-M6)
    ("M1", "Crispy Chicken with Fried Rice",
     "crispy golden fried chicken pieces served on a bed of egg fried rice with scallions, on a white plate"),
    ("M2", "Onion Beef",
     "tender sliced beef stir-fried with caramelized onions and green peppers, glistening sauce, served on a round plate"),
    ("M3", "Orange Duck",
     "crispy roasted duck pieces glazed with bright orange sauce, garnished with orange slices and steamed vegetables"),
    ("M4", "Mala Tofu",
     "cubes of silken tofu swimming in a bright red Sichuan mala chili sauce with dried chilies and Sichuan peppercorns"),
    ("M5", "Vegetable Dumplings",
     "six steamed vegetable dumplings with translucent wrappers showing green filling, served in a bamboo steamer with dipping sauce"),
    ("M6", "Szechuan Pork",
     "sliced pork stir-fried with red and green chilies, dried Sichuan peppers, and crisp vegetables in a dark spicy sauce"),

    # STARTERS (K1-K11)
    ("K1", "Mouth Watering Chicken (KouShuiJi)",
     "poached chicken slices drenched in bright red chili oil with crushed peanuts, sliced scallions, and Sichuan peppercorns on a white oval plate"),
    ("K2", "Spicy Sliced Beef and Tripe (FuQiFeiPian)",
     "thin slices of braised beef and honeycomb tripe fanned out on a plate, coated in red chili oil with sesame seeds and cilantro"),
    ("K3", "Crispy Spareribs (SuPaiGu)",
     "deep-fried golden brown pork spareribs stacked on a plate, glistening with a light glaze, garnished with fried garlic"),
    ("K4", "Spicy Tripe (NiuBaiYe)",
     "sliced beef tripe in a pool of red chili sauce with sliced garlic, chili flakes, and sesame seeds"),
    ("K5", "Smashed Cucumber Salad (PaiHuangGua)",
     "roughly smashed cucumber pieces tossed with garlic, chili oil, and sesame seeds in a shallow dish"),
    ("K6", "Smoked Tofu with Coriander (XiangGan BanDouFu)",
     "slices of brown smoked tofu tossed with fresh cilantro leaves, drizzled with sesame oil and soy dressing"),
    ("K7", "Shredded Potatoes (TuDouSi)",
     "a mound of thin julienned stir-fried potatoes with dried red chilies and green Sichuan peppercorns, slightly crispy"),
    ("K8", "Tiger Peppers (HuPiJiaoJiao)",
     "blistered and charred green shishito-style peppers with blackened spots, served with a savory soy-garlic sauce on the side"),
    ("K9", "Wood Ear Mushroom Salad (LiangBan MuEr)",
     "cold black wood ear mushroom strips tossed with shredded carrots, cilantro, vinegar dressing, and a touch of chili oil"),
    ("K10", "Sweet and Sour Jellyfish (LiangBan HaiZhe)",
     "translucent shredded jellyfish strips in a light sweet vinegar dressing with shredded cucumber and sesame seeds"),
    ("K11", "Homemade Pickled Cabbage (SuanCai)",
     "a small bowl of tangy pale-yellow fermented pickled napa cabbage with red chili flakes on top"),

    # SOUPS (S1-S4)
    ("S1", "TanTan Daily Soup",
     "a steaming bowl of clear Chinese soup with tofu cubes, sliced mushrooms, and leafy greens"),
    ("S2", "Wonton Soup",
     "a bowl of clear broth with plump pork wontons, a few drops of sesame oil, chopped scallions floating on top"),
    ("S3", "Tom Yum Style Soup",
     "a hot and sour soup in a bowl with shrimp, mushrooms, lemongrass, lime leaves, and a reddish chili oil slick"),
    ("S4", "Vegetable Soup",
     "a comforting clear vegetable soup with napa cabbage, carrots, corn, and tofu in a light broth"),

    # DIMSUM (D1-D9)
    ("D1", "Shrimp Har Gow (XiaJiao)",
     "four translucent crystal shrimp dumplings with pink shrimp visible through the delicate wrapper, in a bamboo steamer"),
    ("D2", "Wild Garlic Shrimp DimSum",
     "steamed dim sum dumplings with a green-tinged wild garlic wrapper and shrimp filling, in a bamboo steamer basket"),
    ("D3a", "Pork Shumai",
     "four open-topped siu mai dumplings with yellow wrappers and a pink pork filling, topped with a dot of fish roe, in a steamer"),
    ("D3b", "Chicken Shumai",
     "four open-topped siu mai dumplings with yellow wrappers and a light chicken filling, garnished with a green pea on top"),
    ("D4", "Fried Prawn DimSum (LongXia)",
     "golden deep-fried prawn dim sum pieces with a crispy crunchy exterior, served on a small plate with sweet chili sauce"),
    ("D5", "Beef Curry DimSum",
     "steamed dim sum dumplings with a yellow-tinted curry beef filling, served in a bamboo steamer with curry sauce on the side"),
    ("D6", "Vegetable DimSum",
     "steamed vegetable dim sum dumplings with a green spinach wrapper, showing mixed vegetable filling, in a bamboo steamer"),
    ("D7", "DimSum Platter",
     "an assorted dim sum platter with har gow, siu mai, spring rolls, and fried dumplings arranged on a large plate with dipping sauces"),
    ("D8", "Spring Rolls",
     "four golden crispy fried spring rolls cut diagonally showing the vegetable filling, served with sweet chili dipping sauce"),
    ("D9", "Shrimp Rolls",
     "golden fried shrimp rolls with a crispy wrapper and visible shrimp inside, served on a plate with garnish and dipping sauce"),

    # JIAOZI (T1-T7)
    ("T1", "Vegetable JiaoZi",
     "a plate of pan-fried and steamed vegetable jiaozi dumplings with a golden-brown bottom and white pleated top, with dipping sauce"),
    ("T2", "Chicken JiaoZi",
     "a plate of plump chicken jiaozi dumplings with delicate pleated edges, some pan-fried with golden bottoms, with black vinegar dip"),
    ("T3", "Pork JiaoZi",
     "a plate of juicy pork jiaozi dumplings, some boiled with a glossy skin, arranged neatly with a small dish of soy-vinegar dip"),
    ("T4", "Mixed JiaoZi Platter",
     "a large platter of assorted jiaozi dumplings including boiled, steamed, and pan-fried varieties with multiple dipping sauces"),
    ("T5", "Pan-Fried Buns (ShengJianBao)",
     "four pan-fried soup dumplings with golden crispy bottoms, white fluffy tops sprinkled with black sesame seeds and chopped scallions"),
    ("T6", "Vegetable Steamed Buns",
     "fluffy white steamed bao buns with a vegetable filling, served in a bamboo steamer, soft and pillowy"),
    ("T7", "Chili Oil Wontons (ChaoShou)",
     "silky wontons in a pool of bright red chili oil with garlic, Sichuan pepper, soy sauce, and chopped scallions"),

    # NOODLES (N1-N10)
    ("N1", "Beef Noodle Soup (NiuRouMian)",
     "a large bowl of rich beef broth with hand-pulled wheat noodles, tender braised beef chunks, bok choy, and scallions"),
    ("N2", "Pork Zhajiang Noodles (ZhaJiangMian)",
     "a bowl of thick wheat noodles topped with dark brown minced pork zhajiang sauce, julienned cucumber, and edamame"),
    ("N3", "Chicken Ban Mian (JiSi BanMian)",
     "a bowl of flat wheat noodles in clear broth with shredded chicken, sliced mushrooms, and leafy greens"),
    ("N4", "Duck Noodles",
     "a bowl of egg noodles in a rich duck broth with slices of roasted duck, bok choy, and a soft-boiled egg"),
    ("N5", "Lamb Tomato Noodles",
     "a bowl of hand-pulled noodles in a red tomato-based broth with tender lamb pieces, cilantro, and chili oil"),
    ("N6", "Seafood Noodle Soup",
     "a steaming bowl of noodle soup with shrimp, squid rings, mussels, and vegetables in a clear seafood broth"),
    ("N7", "Dan Dan Noodles (DanDanMian)",
     "a bowl of thin noodles in creamy spicy Sichuan sesame-peanut sauce with minced pork, chili oil, and crushed peanuts"),
    ("N8", "Cold Chicken Noodles (LiangMian)",
     "a plate of cold noodles topped with shredded chicken, cucumber strips, and a sesame-soy dressing, served chilled"),
    ("N9", "Dumpling Soup (HunTun Tang)",
     "a bowl of clear soup with plump wontons/dumplings, dried seaweed flakes, and a drizzle of sesame oil"),
    ("N10", "Tofu Tomato Noodles",
     "a bowl of noodles in a bright red tomato broth with cubes of soft tofu, leafy greens, and a sprinkle of scallions"),

    # MAIN COURSES (H1-H21)
    ("H1", "TanTan Chicken",
     "stir-fried chicken pieces in a savory house-special TanTan sauce with dried chilies, peanuts, and vegetables"),
    ("H2", "Mixed Vegetable Chicken",
     "tender chicken breast slices stir-fried with colorful mixed vegetables like broccoli, carrots, bell peppers, and snap peas"),
    ("H3", "Scallion Beef",
     "sliced tender beef stir-fried with plenty of green scallion segments in a savory soy-based sauce"),
    ("H4", "Boiled Beef in Chili Oil (ShuiZhuNiuRou)",
     "thin slices of beef submerged in a fiery red Sichuan chili oil broth with bean sprouts, dried chilies, and Sichuan peppercorns, served in a large bowl"),
    ("H5", "Sour Soup Beef (SuanTang NiuRou)",
     "sliced beef in a tangy golden sour broth with pickled peppers, tomatoes, and enoki mushrooms"),
    ("H6", "Sizzling Lamb (TieBan YangRou)",
     "sliced lamb sizzling on a hot iron plate with onions, peppers, and cumin, steam rising from the plate"),
    ("H7", "Cumin Lamb (ZiRan YangRou)",
     "tender lamb pieces stir-fried with generous cumin seeds, dried red chilies, sliced onions, and cilantro"),
    ("H8", "Twice-Cooked Pork (HuiGuoRou)",
     "slices of pork belly stir-fried with leeks, green peppers, and fermented black bean sauce, slightly caramelized"),
    ("H9", "TanTan Sweet and Sour Pork",
     "golden crispy pork pieces coated in a glossy red-orange sweet and sour sauce with pineapple chunks and bell pepper"),
    ("H10", "Crispy Duck (XiangSuYa)",
     "half a crispy roasted duck with mahogany-brown lacquered skin, served on a platter with steamed buns and hoisin sauce"),
    ("H11", "Mango Duck (MangoYa)",
     "crispy roasted duck pieces topped with a bright yellow mango sauce and fresh mango chunks"),
    ("H12", "Red Curry Duck",
     "sliced duck in a rich red Thai-style curry sauce with coconut milk, bamboo shoots, and Thai basil"),
    ("H13", "Home-Style Tofu (JiaChang DouFu)",
     "pan-fried golden tofu slices braised with sliced pork, wood ear mushrooms, and leeks in a savory sauce"),
    ("H14", "Mapo Tofu (MaPo DouFu)",
     "soft white tofu cubes in a bubbling red-brown Sichuan sauce with minced pork, fermented bean paste, chili oil, and Sichuan peppercorns"),
    ("H15", "Spicy Eggplant (YuXiang QieZi)",
     "tender Chinese eggplant pieces in a glossy red yuxiang sauce with minced pork, garlic, ginger, and scallions"),
    ("H16", "Three Treasures (DiSanXian)",
     "chunks of fried potato, eggplant, and green bell pepper stir-fried together in a savory garlic-soy sauce"),
    ("H17", "Shiitake Bok Choy (XiangGu CaiXin)",
     "baby bok choy hearts arranged on a plate with braised shiitake mushrooms in an oyster sauce glaze"),
    ("H18", "Salt and Pepper Prawns (JiaoYan XiaRen)",
     "crispy fried whole prawns coated with salt, white pepper, diced chilies, and garlic in a dry stir-fry"),
    ("H19", "TanTan Tomato Fish (FanQie Yu)",
     "flaky white fish fillets in a bright red tomato-based sauce with cherry tomatoes, garlic, and fresh herbs"),
    ("H20", "Pickled Cabbage Fish (SuanCai Yu)",
     "tender white fish fillets in a tangy yellow broth with pickled mustard greens, Sichuan peppercorns, and dried chilies"),
    ("H21", "Boiled Fish in Chili (ShuiZhu Yu)",
     "sliced white fish fillets swimming in a bright red Sichuan chili oil broth with bean sprouts, dried chilies, and a mountain of Sichuan peppercorns"),

    # SIDES/DESSERTS (B1-B6)
    ("B1", "Jasmine Rice (MiFan)",
     "a small bowl of fluffy steamed white jasmine rice with a slightly sticky texture"),
    ("B2", "Fried Rice small (ChaoFan)",
     "a plate of golden egg fried rice with diced scallions, peas, and small pieces of egg, served in a small portion"),
    ("B2G", "Fried Rice large (ChaoFan)",
     "a generous plate of golden egg fried rice with scrambled egg bits, green peas, diced carrots, and scallions"),
    ("B4", "Baked Alaska Ice Cream (HuoBingQiu)",
     "a flambeed baked Alaska dessert with golden meringue exterior, slightly torched, on a plate with a sparkler"),
    ("B5", "Pumpkin Rice Cake (NanGuaBing)",
     "golden pan-fried pumpkin rice cakes with a crispy exterior and soft chewy interior, dusted with sesame seeds"),
    ("B6", "Brown Sugar Rice Cake (HongTangCiBa)",
     "chewy mochi-like rice cakes drizzled with dark brown sugar syrup and coated with soybean flour"),
]

MODELS = {
    "grok-imagine-image": {"cost": 0.02, "rpm": 300},
    "grok-2-image-1212": {"cost": 0.07, "rpm": 300},
    "grok-imagine-image-pro": {"cost": 0.07, "rpm": 30},
}

API_URL = "https://api.x.ai/v1/images/generations"


def build_prompt(name: str, description: str) -> str:
    """Build a natural-looking food photo prompt for Grok."""
    return (
        f"Photorealistic image of {name} from the Chinese restaurant TanTan in Vienna, "
        f"{description}. Wide shot showing the ENTIRE plate centered on a dark wood table, "
        f"photographed from a 45-degree angle sitting across the table. "
        f"The plate takes up about 40% of the frame. "
        f"Table surface visible, chopsticks nearby, blurred restaurant interior background. "
        f"Warm ambient lighting, natural depth of field, casual phone photo. "
        f"Do NOT zoom in close. Show the full scene with surroundings."
    )


def generate_image(api_key: str, prompt: str, model: str, retries: int = 3) -> str:
    """Call xAI Image API and return the image URL."""
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(
                API_URL,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model, "prompt": prompt, "n": 1},
                timeout=60,
            )
            resp.raise_for_status()
            result = resp.json()

            if "data" in result and len(result["data"]) > 0:
                url = result["data"][0].get("url")
                if url:
                    return url

            raise RuntimeError(f"No image URL in response: {json.dumps(result)[:200]}")

        except Exception as e:
            last_error = e
            if attempt < retries:
                wait = 2 ** attempt
                print(f"      Retry {attempt}/{retries - 1} in {wait}s: {e}")
                time.sleep(wait)

    raise RuntimeError(f"Failed after {retries} attempts: {last_error}")


def download_and_save(url: str, output_path: Path) -> None:
    """Download image from URL, resize to 800x800 square, save as JPEG."""
    from PIL import Image

    img_resp = requests.get(url, timeout=60)
    img_resp.raise_for_status()
    img = Image.open(io.BytesIO(img_resp.content))
    img = img.convert("RGB")
    # Center-crop to square, then resize to 800x800
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((800, 800), Image.LANCZOS)
    img.save(str(output_path), "JPEG", quality=82)


def main():
    parser = argparse.ArgumentParser(
        description="Generate food images for TanTan menu using xAI Grok Image API"
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("XAI_API_KEY", ""),
        help="xAI API key (or set XAI_API_KEY env var)",
    )
    parser.add_argument(
        "--model",
        default="grok-2-image-1212",
        choices=list(MODELS.keys()),
        help="Which Grok image model to use (default: grok-2-image-1212)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate images even if they already exist",
    )
    parser.add_argument(
        "--items",
        nargs="+",
        default=None,
        help="Generate only specific item codes (e.g. --items M1 K1 H4)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview prompts without making API calls",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay in seconds between API requests (default: 0.5)",
    )
    parser.add_argument(
        "--output-dir",
        default="./images",
        help="Output directory for generated images (default: ./images)",
    )
    args = parser.parse_args()

    if not args.dry_run and not args.api_key:
        print("ERROR: No API key provided. Use --api-key or set XAI_API_KEY env var.")
        print("Sign up at console.x.ai for $25 free credits.")
        sys.exit(1)

    # Filter items
    items = MENU_ITEMS
    if args.items:
        filter_set = {code.upper() for code in args.items}
        items = [(code, name, desc) for code, name, desc in MENU_ITEMS if code in filter_set]
        not_found = filter_set - {code for code, _, _ in items}
        if not_found:
            print(f"WARNING: Item codes not found: {', '.join(sorted(not_found))}")
        if not items:
            print("ERROR: No matching items found.")
            sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model_info = MODELS[args.model]
    total = len(items)
    generated = 0
    skipped = 0
    failed = 0
    failed_items = []

    print(f"TanTan Menu Image Generator (Grok)")
    print(f"{'=' * 55}")
    print(f"Model:  {args.model} (${model_info['cost']}/image, {model_info['rpm']} RPM)")
    print(f"Items:  {total}  |  Output: {output_dir.resolve()}  |  Delay: {args.delay}s")
    if args.dry_run:
        print("MODE: DRY RUN (no API calls)")
    if args.force:
        print("MODE: FORCE (overwriting existing images)")
    print()

    start_time = time.time()

    for idx, (code, name, description) in enumerate(items, 1):
        output_path = output_dir / f"{code}.jpg"
        prompt = build_prompt(name, description)

        if output_path.exists() and not args.force:
            print(f"[{idx}/{total}] {code} - {name} ... SKIPPED (exists)")
            skipped += 1
            continue

        if args.dry_run:
            print(f"[{idx}/{total}] {code} - {name}")
            print(f"  Prompt: {prompt[:120]}...")
            print(f"  Output: {output_path}")
            print()
            generated += 1
            continue

        item_start = time.time()
        try:
            print(f"[{idx}/{total}] {code} - {name} ... ", end="", flush=True)
            image_url = generate_image(args.api_key, prompt, args.model, retries=3)
            download_and_save(image_url, output_path)
            elapsed = time.time() - item_start
            file_size_kb = output_path.stat().st_size / 1024
            print(f"OK ({elapsed:.1f}s, {file_size_kb:.0f}KB)")
            generated += 1
        except Exception as e:
            elapsed = time.time() - item_start
            print(f"FAILED ({elapsed:.1f}s) - {e}")
            failed += 1
            failed_items.append(code)

        if idx < total and args.delay > 0:
            time.sleep(args.delay)

    total_time = time.time() - start_time

    print()
    print(f"{'=' * 55}")
    print(f"SUMMARY")
    print(f"{'=' * 55}")
    print(f"  Generated: {generated}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")
    if failed_items:
        print(f"  Failed items: {', '.join(failed_items)}")
    print(f"  Total time: {total_time:.1f}s")

    est_cost = generated * model_info["cost"]
    label = "Est. cost" if not args.dry_run else "Est. cost (if run)"
    print(f"  {label}:  ${est_cost:.3f} ({generated} images x ${model_info['cost']}/image)")
    print()

    if failed > 0:
        print(f"TIP: Re-run failed items with: --items {' '.join(failed_items)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
