#!/usr/bin/env python3
"""
TanTan Chinese Fine Dining - Menu Generator
Generates a beautiful, self-contained HTML menu for TanTan restaurant in Vienna.
Usage: python build_tantan_menu.py
Output: TanTan_Menu.html (auto-opens in browser)
"""

import os
import sys
import base64
import webbrowser
import html as html_mod
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
IMAGES_DIR = SCRIPT_DIR / "images"
OUTPUT_FILE = SCRIPT_DIR / "TanTan_Menu.html"

# ---------------------------------------------------------------------------
# Allergen master list
# ---------------------------------------------------------------------------
ALLERGEN_MAP = {
    "A": "Glutenhaltiges Getreide",
    "B": "Krebstiere",
    "C": "Eier von Gefl\u00fcgel",
    "D": "Fisch",
    "E": "Erdn\u00fcsse",
    "F": "Sojabohnen",
    "G": "Milchprodukte inkl. Laktose",
    "H": "Schalenfrüchte",
    "L": "Sellerie",
    "M": "Senf",
    "N": "Sesam",
    "O": "Schwefeldioxid und Sulfite",
    "P": "Lupinen",
    "R": "Weichtiere (Muschel, Tintenfisch\u2026)",
}

# Placeholder gradient colours per section prefix
GRADIENT_MAP = {
    "M": ("#c41e3a", "#8b0000"),
    "K": ("#ff6b6b", "#ee5a24"),
    "S": ("#fdcb6e", "#e17055"),
    "D": ("#e17055", "#c44569"),
    "T": ("#e17055", "#c44569"),
    "N": ("#fdcb6e", "#e17055"),
    "H": ("#c41e3a", "#8b0000"),
    "B": ("#e8a87c", "#d4956b"),
}


# ---------------------------------------------------------------------------
# Menu data  (code, name, chinese, english_name, allergens, price, de, en)
# ---------------------------------------------------------------------------
# For items that have no separate english_name column, set it to ""

def _mi(code, name, chinese, english_name, allergens, price, de, en):
    """Menu item helper."""
    return {
        "code": code,
        "name": name,
        "chinese": chinese,
        "english_name": english_name,
        "allergens": allergens,
        "price": price,
        "de": de,
        "en": en,
    }


FOOD_SECTIONS = [
    # ---- SECTION 1: TanTan Lunch ----
    {
        "title": "TanTan Lunch",
        "chinese": "\u5348\u9910",
        "note": "Montag bis Freitag 11:00\u201315:00 \u00b7 inkl. Tagessuppe oder MiniRollen und Beilage",
        "note2": "Getr\u00e4nke zum Men\u00fc: Hausgemachte TanTan Limonade 0.30L +2,00\u20ac",
        "items": [
            _mi("M1", "Crispy Chicken", "\u9999\u9165\u9e21\u7092\u996d", "", "A C F N", "10,90",
                 "Knusprige H\u00fchnerfleisch / Gebe. Eierreis",
                 "crispy chicken / fried rice"),
            _mi("M2", "Onion Beef", "\u6d0b\u8471\u725b\u8089", "", "A F N", "11,90",
                 "Rindfleisch / Zwiebel",
                 "beef / onion"),
            _mi("M3", "Orang Duck", "\u6a59\u5b50\u9e2d", "", "A C F N", "10,90",
                 "Knusprige Ente / Orange / Saisonales Gem\u00fcse / S\u00fcss Pikant",
                 "Crispy duck / orange / seasonal vegetables / sweet spice"),
            _mi("M4", "Mala DouFu", "\u9ebb\u8fa3\u8c46\u8150", "", "A F N", "10,90",
                 "Tofu / Chili / Saisonales Gem\u00fcse / vegan",
                 "tofu / chili / seasonal vegetables / vegan"),
            _mi("M5", "SuJiaoZi", "\u7d20\u997a\u5b50", "", "A F N", "10,90",
                 "Teigtaschen / Morcheln / Shiitake / Gem\u00fcse / 9 St\u00fccke",
                 "dumpling / morels / shiitake / vegetables / 9 pieces"),
            _mi("M6", "SzeChuan Pork", "\u56db\u5ddd\u732a\u8089", "", "A F N", "11,90",
                 "Schweinefleisch / Chili / Gem\u00fcse",
                 "Pork / chili / vegetables"),
        ],
    },
    # ---- SECTION 2: Starters ----
    {
        "title": "Kaiweicai \u00b7 Starter",
        "chinese": "\u5f00\u80c3\u83dc",
        "note": "",
        "note2": "",
        "items": [
            _mi("K1", "KouShuiJi", "\u53e3\u6c34\u9e21", "Mouth Watering Chicken", "A E F N", "7,90",
                 "Marinierte H\u00fchnerkeulenfleisch / hausgemachtes Chili-\u00d6l",
                 "marinated chicken / boneless / self-made chili oil"),
            _mi("K2", "FuQiFeiPian", "\u592b\u59bb\u80ba\u7247", "Spicy Sliced Beef & Tripe", "A E F N", "9,90",
                 "Rindfleisch / Kutteln / hausgemachte Chili-\u00d6l / Koriander",
                 "beef / tripe / self-made chili oil / coriander"),
            _mi("K3", "SuPaiGu", "\u9165\u6392\u9aa8", "Knusprige Spareribs", "A C F G H N", "8,90",
                 "Knusprig Frittierte MiniSchweinsRippchen / TanTanSauce",
                 "crispy fried minispareribs / homemade TanTan sauce"),
            _mi("K4", "NiuBaiYe", "\u725b\u767e\u53f6", "Spicy Tripe", "A F N", "8,90",
                 "RindKutteln / hausgemachte Chili-\u00d6l / Koriander",
                 "beef tripe / self-made Chili oil / coriander"),
            _mi("K5", "PaiHuangGua", "\u62cd\u9ec4\u74dc", "Smashed Cucumber Salad", "A F N", "6,50",
                 "Gurken / Knoblauch / hausgemachte TanTan Sauce / Chili-\u00d6l",
                 "cucumber / garlic / homemade TanTan sauce / self-made Chili oil"),
            _mi("K6", "XianCaiGanSi", "\u9999\u83dc\u5e72\u4e1d", "Ger\u00e4ucherter Tofu", "A F L N", "6,90",
                 "Ger\u00e4ucherter Tofu / Koriander",
                 "smoked Tofu / coriander"),
            _mi("K7", "LiangBanTuDouSi", "\u51c9\u62cc\u571f\u8c46\u4e1d", "Shredded Potatoes", "F N", "6,50",
                 "Knackige Kartoffelstreifen / hausgemachtes Chili-\u00d6l / Reisessig / Koriander",
                 "crispy shredded potatoes / self-made chili oil / rice vinegar / coriander"),
            _mi("K8", "HuPiQingJiao", "\u864e\u76ae\u9752\u6912", "Tiger Peppers", "A F N", "6,90",
                 "scharfe Pfefferoni / schwarze BohnenSauce",
                 "chili pepper / black bean sauce"),
            _mi("K9", "BanMuEr", "\u62cc\u6728\u8033", "Morel Salad", "A F N", "6,90",
                 "Morcheln / MiniChili / Reisessig",
                 "morels / minichili / rice vinegar"),
            _mi("K10", "TangCuHaiZhe", "\u7cd6\u918b\u6d77\u86f0", "Sweet & Sour Jellyfish", "F N", "9,90",
                 "Qualle / S\u00fc\u00dfSauer Sauce / Honig / Koriander",
                 "jellyfish / sweet sour sauce / honey / coriander"),
            _mi("K11", "PaoCai", "\u6ce1\u83dc", "Homemade Cabbage", "O", "6,50",
                 "fermentierter ChinaKohl / Rettich / Lauch / Knoblauch / Chili-\u00d6l",
                 "fermented chinese cabbage / radish / leek / garlic / self-made chili oil"),
        ],
    },
    # ---- SECTION 3: Suppe ----
    {
        "title": "Tang \u00b7 Suppe",
        "chinese": "\u6c64",
        "note": "",
        "note2": "",
        "items": [
            _mi("S1", "TanTan TagesSuppe", "", "Daily Soup", "A F", "4,50",
                 "saisonal wechselnde Suppe",
                 "seasonal changing soup"),
            _mi("S2", "YunDungTang", "\u4e91\u7096\u6c64", "WonTon Suppe", "A B D F", "5,50",
                 "H\u00fchnerfleisch WonTon / saisonales Gem\u00fcse",
                 "chicken wonton / seasonal vegetables"),
            _mi("S3", "DongYinGon", "\u51ac\u9634\u529f\u6c64", "Tom Yum Soup", "B D F R", "6,90",
                 "Garnelen / Gem\u00fcse / sehr scharf",
                 "shrimps / vegetable / very spicy"),
            _mi("S4", "ShuCaiTang", "\u852c\u83dc\u6c64", "Vegetable Soup", "F", "5,50",
                 "Saisonales Gem\u00fcse",
                 "seasonal vegetables"),
        ],
    },
    # ---- SECTION 4: DimSum ----
    {
        "title": "Dianxin \u00b7 DimSum",
        "chinese": "\u70b9\u5fc3",
        "note": "Alle DimSum sind hausgemacht / all DimSum are home-made",
        "note2": "Alle DimSum serviert mit hausgemachter Sauce A C M",
        "items": [
            _mi("D1", "XiaJiao", "\u867e\u997a", "Shrimp DimSum", "B D F N", "6,90",
                 "ged\u00e4mpfte DimSum / Garnelen / Bambus / 3 St\u00fcck",
                 "steamed DimSum / shrimps / bamboo / 3 pieces"),
            _mi("D2", "JiuCaiJiao", "\u97ed\u83dc\u997a", "Wild Garlic DimSum", "B D F N", "6,90",
                 "ged\u00e4mpfte DimSum / Garnelen / B\u00e4rlauch / 3 St\u00fcck",
                 "steamed DimSum / shrimps / wild garlic / 3 pieces"),
            _mi("D3a", "ShaoMai (Pork)", "\u70e7\u5356", "Pork ShaoMai", "A B D F N", "6,90",
                 "ged\u00e4mpfte ShaoMai DimSum / SchweineFleisch / Garnelen / 4 St\u00fcck",
                 "steamed ShaoMai DimSum / pork / shrimps / 4 pieces"),
            _mi("D3b", "ShaoMai (Chicken)", "\u9e21\u8089\u70e7\u5356", "Chicken ShaoMai", "A B D F N", "6,90",
                 "ged\u00e4mpfte ShaoMai DimSum / H\u00fchnerFleisch / 4 St\u00fcck",
                 "steamed ShaoMai DimSum / chicken / 4 pieces"),
            _mi("D4", "LongXiaJiao", "\u9f99\u867e\u997a", "Fried LongXia DimSum", "A B D F N", "6,90",
                 "gebackene LongXia DimSum / Schweinefleisch / Garnelen / 4 St\u00fcck",
                 "fried LongXia DimSum / pork / shrimps / 4 pieces"),
            _mi("D5", "GaLiJiao", "\u725b\u8089\u5496\u55b1\u997a", "Beef Curry DimSum", "A B C D F N", "6,90",
                 "gebackene DimSum / RindFleisch / Curry / 2 St\u00fcck",
                 "fried DimSum / beef / curry / 2 pieces"),
            _mi("D6", "SuFenGuo", "\u7d20\u7c89\u679c", "Vegetable DimSum", "A E F L N V", "6,90",
                 "ged\u00e4mpfte DimSum / Erdnuss / Saisonalem Gem\u00fcse / 3 St\u00fcck",
                 "steamed DimSum / peanut / seasonal vegetables / 3 pieces"),
            _mi("D7", "DianXinPinPan", "\u70b9\u5fc3\u62fc\u76d8", "DimSum Platter", "A B E D F L N V", "24,90",
                 "DimSum Mix / 12 St\u00fcck (je 2 St\u00fcck von D1\u2013D3, D4\u2013D6)",
                 "DimSum Variation / 12 pieces (2 pieces each from D1\u2013D3, D4\u2013D6)"),
            _mi("D8", "SuChunJuan", "\u7d20\u6625\u5377", "Spring Rolls", "A D F L N", "4,90",
                 "Handgemachte Fr\u00fchlingsrolle / Saisonales Gem\u00fcse / 2 St\u00fcck",
                 "home-made spring rolls / seasonal vegetables / 2 pieces"),
            _mi("D9", "XiaHeZi", "\u867e\u76d2\u5b50", "Shrimp Rolls", "A B D F N", "6,90",
                 "gebackene DimSumRolle / Garnelen / Wasserkastanie / 2 St\u00fcck",
                 "fried DimSum rolls / shrimps / water chestnut / 2 pieces"),
        ],
    },
    # ---- SECTION 5: JiaoZi ----
    {
        "title": "JiaoZi \u00b7 Dumplings",
        "chinese": "\u997a\u5b50",
        "note": "Alle JiaoZi sind hausgemacht / all JiaoZi are home-made",
        "note2": "",
        "items": [
            _mi("T1", "SuJiaoZi", "\u7d20\u997a\u5b50", "Vegetable Dumplings", "A F N", "6,90",
                 "Teigtaschen / ChinaKohl / Morcheln / Shiitake / Jungzwiebeln / 6 St\u00fcck",
                 "dumpling / cabbage / morels / Shiitake / young onion / 6 pieces"),
            _mi("T2", "JiRouJiaoZi", "\u9e21\u8089\u997a\u5b50", "Chicken Dumplings", "A F N", "6,90",
                 "Teigtaschen / H\u00fchnerfleisch / 6 St\u00fcck",
                 "dumpling / chicken / 6 pieces"),
            _mi("T3", "ZhuRouJiaoZi", "\u732a\u8089\u997a\u5b50", "Pork Dumplings", "A F N", "6,90",
                 "Teigtaschen / Schweinefleisch / 6 St\u00fcck",
                 "dumpling / pork / 6 pieces"),
            _mi("T4", "ShiJinJiaoZi", "\u4ec0\u9526\u997a\u5b50", "Mixed Dumplings", "A F N", "6,90",
                 "Teigtaschen Variation / 6 St\u00fcck / (je 2 St\u00fcck von T1 bis T3)",
                 "dumpling variation / 6 pieces / (2 pieces each from T1 to T3)"),
            _mi("T5", "ShengJianBao", "\u751f\u714e\u5305", "Pan-Fried Buns", "A F N", "5,90",
                 "HefeTeigtaschen / Schweinefleisch / 4 St\u00fcck",
                 "yeast dough dumpling / pork / 4 pieces"),
            _mi("T6", "SuXiaoLongBao", "\u7d20\u5c0f\u7b3c\u5305", "Vegetable Buns", "A F N", "5,90",
                 "HefeTeigtaschen / Gem\u00fcse / 4 St\u00fcck",
                 "yeast dough dumpling / vegetable / 4 pieces"),
            _mi("T7", "HongYouChaoShou", "\u7ea2\u6cb9\u6284\u624b", "Chili Oil Wontons", "A F N", "5,90",
                 "WonTon / H\u00fchnerfleisch / hausgemachte Chili \u00d6l / 5 St\u00fcck",
                 "wonton / chicken / self-made chili oil / 5 pieces"),
        ],
    },
    # ---- SECTION 6: Nudeln ----
    {
        "title": "Mian \u00b7 Nudeln",
        "chinese": "\u9762",
        "note": "Alle Nudeln sind frisch hausgemacht / all noodles are freshly home-made",
        "note2": "",
        "items": [
            _mi("N1", "HongShaoNiuRouMian", "\u7ea2\u70e7\u725b\u8089\u9762", "Beef Noodle Soup", "A F N", "15,90",
                 "NudelSuppe / Rindfleisch / Chili \u00d6l / Koriander (w\u00e4hlbar ohne Suppe)",
                 "noodleSoup / beef / self-made chili oil / coriander (possible without soup)"),
            _mi("N2", "ZhuPaiZhaJiangMian", "\u732a\u6392\u7092\u9171\u9762", "Pork Noodles", "A C F N", "14,90",
                 "Schweineschnitzel / SojaBohnenPaste / Saisonales Gem\u00fcse",
                 "pork chops / soja bean paste / seasonal vegetables"),
            _mi("N3", "TanTanBanMian", "\u9e21\u6392\u62cc\u9762", "Chicken Noodles", "A C F N", "14,90",
                 "H\u00fchnerschnitzel / Chili-PaprikaPaste / Saisonales Gem\u00fcse",
                 "chicken chops / chili-pepper paste / seasonal vegetables"),
            _mi("N4", "YaZiBanMian", "\u9e2d\u5b50\u62cc\u9762", "Duck Noodles", "A F N", "15,90",
                 "Knusprige Ente / Saisonales Gem\u00fcse / TanTan Sauce",
                 "crispy duck / seasonal vegetables / TanTan sauce"),
            _mi("N5", "FanQieYangRouBanMian", "\u756a\u8304\u7f8a\u8089\u62cc\u9762", "Lamb Noodles", "A F N", "15,90",
                 "Lammfleisch / Tomaten / Koriander",
                 "lamb / tomatoes / coriander"),
            _mi("N6", "TanTanHaiXianMian", "\u6d77\u9c9c\u9762", "Seafood Noodles", "A B F D N R", "16,90",
                 "NudelSuppe / Garnelen / Tintenfisch / Surimi / Gr\u00fcnschalMuschel / Koriander",
                 "noodleSoup / shrimps / squid / surimi / greenshell mussels / coriander"),
            _mi("N7", "SiChuanDanDanMian", "\u56db\u5ddd\u62c5\u62c5\u9762", "Dan Dan Noodles", "A E F N", "13,90",
                 "FaschiertesSchweinefleisch oder Vegan / Chili \u00d6l / Koriander / Erdnuss",
                 "minced pork possible VEGAN / self-made chili oil / coriander / peanut"),
            _mi("N8", "JiRouHongYouLiangMian", "\u9e21\u8089\u7ea2\u6cb9\u51c9\u9762", "Cold Chicken Noodles", "A F N", "14,90",
                 "H\u00fchnerfleisch / Gurke / Chili \u00d6l / Koriander / Kalte nudeln",
                 "chicken / cucumber / self-made chili oil / coriander / cold noodle"),
            _mi("N9", "SuanTangJiaoZi", "\u9178\u6c64\u997a\u5b50", "Dumpling Soup", "A F N", "13,90",
                 "Suppe mit Teigtaschen / Chili / Koriander / 10 St\u00fcck",
                 "soup with dumpling / chili / coriander / 10 pieces"),
            _mi("N10", "XiHongShiDouFuBanMian", "\u897f\u7ea2\u67ff\u8c46\u8150\u62cc\u9762", "Tofu Tomato Noodles", "A F N", "13,50",
                 "Tofu / Tomaten / Koriander",
                 "Tofu / tomatoes / coriander"),
        ],
    },
    # ---- SECTION 7: Main Course ----
    {
        "title": "Zhengcai \u00b7 Hauptspeise",
        "chinese": "\u6b63\u83dc",
        "subtitle": "Main Course",
        "note": "",
        "note2": "",
        "items": [
            _mi("H1", "TanTanJi", "TanTan\u9e21", "TanTan Chicken", "A F N", "14,90",
                 "H\u00fchnerfleisch / Zucchini / Chilli / TanTan Sauce",
                 "chicken / zucchini / chilli / TanTan Sauce"),
            _mi("H2", "ShiJinJi", "\u4ec0\u9526\u9e21", "Mixed Chicken", "A F", "13,90",
                 "H\u00fchnerfleisch / Saisonales Gem\u00fcse",
                 "chicken / seasonal vegetables"),
            _mi("H3", "CongBaoNiuRou", "\u8471\u7206\u725b\u8089", "Scallion Beef", "A F", "15,90",
                 "Rindfleisch / Jungzwiebeln / Saisonales Gem\u00fcse",
                 "beef / young onion / seasonal vegetables"),
            _mi("H4", "ShuiZhuNiuRou", "\u6c34\u716e\u725b\u8089", "Boiled Beef in Chili", "A F N", "17,90",
                 "Rindfilet / geschmoren in ChiliSuppe / Saisonales Gem\u00fcse",
                 "beef / braised in chili soup / seasonal vegetables"),
            _mi("H5", "SuanTangNiuRou", "\u9178\u6c64\u725b\u8089", "Sour Soup Beef", "A F N", "17,90",
                 "Rindfleisch in saurer ChiliSuppe / Gurke / Champignon / K\u00fcrbisSauce",
                 "beef in sour chili soup / cucumber / champignon / pumpkin sauce"),
            _mi("H6", "TieBanYangRou", "\u94c1\u677f\u7f8a\u8089", "Sizzling Lamb", "A F", "17,90",
                 "Lammfleisch / serviert auf hei\u00dfer Gusseisenplatte / Saisonales Gem\u00fcse",
                 "lamb / served on hot iron plate / seasonal vegetables"),
            _mi("H7", "ZiRanYangRou", "\u5b5c\u7136\u7f8a\u8089", "Cumin Lamb", "A F N", "17,90",
                 "Lammfleisch / K\u00fcmmel / Chili",
                 "lamb / cumin / chili"),
            _mi("H8", "HuiGuoRou", "\u56de\u9505\u8089", "Twice-Cooked Pork", "A F N", "15,90",
                 "Bauchfleisch / scharf Pfefferoni / Karotte / SojaBohnenSauce",
                 "pork belly / chili pepper / carrot / soya bean sauce"),
            _mi("H9", "TanTanTangCuRou", "TANTAN\u7cd6\u918b\u8089", "Sweet & Sour Pork", "A F N", "15,90",
                 "Schweinfleisch / PaprikaPaste / S\u00fcsslich",
                 "pork chops / pepper paste / sweet"),
            _mi("H10", "XiangShuYa", "\u9999\u9165\u9e2d", "Crispy Duck", "A C F N", "15,90",
                 "Knusprige Ente / Sojabohnen",
                 "crispy duck / soya bean"),
            _mi("H11", "MangGuoYa", "\u8292\u679c\u9e2d", "Mango Duck", "A C F N", "15,90",
                 "Ente / Mango / LimettenSauce / Saisonales Gem\u00fcse",
                 "duck / mango / lime sauce / seasonal vegetables"),
            _mi("H12", "HongGaLiYa", "\u7ea2\u5496\u55b1\u9e2d", "Red Curry Duck", "A C F N", "15,90",
                 "Ente / Red ChiliCurry / Kokosmilch / Lemongrass / Saisonales Gem\u00fcse",
                 "duck / red chilli curry / coconut milk / lemongrass / seasonal vegetables"),
            _mi("H13", "JiaChangDouFu", "\u5bb6\u5e38\u8c46\u8150", "Home-Style Tofu", "A F", "12,90",
                 "Tofu / Saisonales Gem\u00fcse / vegan",
                 "tofu / seasonal vegetables / vegan"),
            _mi("H14", "MaPoDouFu", "\u9ebb\u5a46\u8c46\u8150", "Mapo Tofu", "A F N", "12,90",
                 "Tofu / hausgemachtes Chili \u00d6l / Pfeffer / Jungzwiebeln / vegan",
                 "tofu / homemade chili oil / pepper / young onion / vegan"),
            _mi("H15", "YuXiangQieZi", "\u9c7c\u9999\u8304\u5b50", "Spicy Eggplant", "A F N", "12,90",
                 "Melanzani / hausgemachtes Chili \u00d6l / SojaBohnenSauce / vegan",
                 "eggplant / homemade chili oil / SojabeanSauce / vegan"),
            _mi("H16", "DiSanXian", "\u5730\u4e09\u9c9c", "Three Treasures", "A F", "12,90",
                 "Paprika / Melanzani / Kartoffeln / vegan",
                 "pepper / eggplant / potato / vegan"),
            _mi("H17", "XiangGuChaoQingCai", "\u9999\u83c7\u7092\u9752\u83dc", "Mushroom Bok Choy", "A F", "12,90",
                 "Pak Choi / Shiitake Pilz / vegan",
                 "pak choi / shiitake mushroom / vegan"),
            _mi("H18", "JiaoYanDaXia", "\u6912\u76d0\u5927\u867e", "Salt & Pepper Prawns", "A E F N", "19,90",
                 "Riesengarnelen / Pfefferbl\u00fctensalz / Erdnuss",
                 "prawn / pepper blossom salt / peanut"),
            _mi("H19", "TanTanFanQieYu", "TANTAN\u756a\u8304\u9c7c", "TanTan Tomato Fish", "A D F", "32,00",
                 "Amurfisch / TomatenSauce / Saisonales Gem\u00fcse",
                 "Amur fish / tomato sauce / seasonal vegetables"),
            _mi("H20", "SuanCaiYu", "\u9178\u83dc\u9c7c", "Pickled Cabbage Fish", "A D F N", "32,00",
                 "Amurfisch / chinesischer Sauerkraut / ChiliSchoten",
                 "Amur fish / chinese fermented cabbage / chili peppers"),
            _mi("H21", "ShuiZhuYu", "\u6c34\u716e\u9c7c", "Boiled Fish in Chili", "A F N", "32,00",
                 "Amurfisch / ChiliSchoten / Saisonales Gem\u00fcse",
                 "Amur fish / chili pepper / seasonal vegetables"),
        ],
    },
    # ---- SECTION 8: Beilage / Desserts ----
    {
        "title": "Beilage / Desserts",
        "chinese": "\u7c73\u996d/\u7518\u70b9",
        "note": "",
        "note2": "",
        "items": [
            _mi("B1", "MiFan", "\u7c73\u996d", "Jasmin Reis", "", "2,20", "", ""),
            _mi("B2", "ChaoFan", "\u7092\u996d", "Gebr. EierReis (klein)", "C", "4,90", "", ""),
            _mi("B2G", "ChaoFan", "\u7092\u996d", "Gebr. EierReis (gross)", "C", "7,90", "", ""),
            _mi("B4", "HuoBingQiu", "\u706b\u51b0\u7403", "Alaska Eiscreme flamb.", "A C E N O", "5,90", "", ""),
            _mi("B5", "NanGuaBing", "\u5357\u74dc\u997c", "K\u00fcrbis Reisteig", "", "5,90", "", ""),
            _mi("B6", "HongTangCiBa", "\u7ea2\u7cd6\u7ccd\u7c91", "Reisteig mit Brauner Zucker", "", "5,90", "", ""),
        ],
    },
]

# ---------------------------------------------------------------------------
# Drink sections (simple list, no images)
# ---------------------------------------------------------------------------
DRINK_SECTIONS = [
    {
        "title": "TanTan Wein Keller",
        "chinese": "\u7ea2\u767d\u9152",
        "allergens": "",
        "items": [
            ("Scheiblhofer Big John Cuv\u00e9e Reserve", "50,00", "Zweigelt trocken 14%vol 0,75l"),
            ("M\u00fcller Gr\u00fcner Veltliner", "37,00", "Gr\u00fcner Veltliner 12,50%vol 0,75l"),
            ("H\u00e4ndler Chardonnay", "40,00", "Chardonnay 13,50%vol 0,75l"),
        ],
    },
    {
        "title": "Alkoholfrei / Softdrinks",
        "chinese": "\u996e\u6599",
        "allergens": "",
        "items": [
            ("Soda / Soda Zitrone", "0,30L 2,50/2,70 \u00b7 0,50L 3,50/3,80", ""),
            ("Holunder/Himbeer SODA", "0,30L 2,90 \u00b7 0,50L 4,20", ""),
            ("Mineral mit/ohne", "0,33L 3,50", ""),
            ("Coca Cola / Zero / Sprite / Fanta / Almdudler", "0,33Fl 3,90", ""),
            ("Cola / Zero / Sprite / Fanta / Almdudler / Spezi", "0,50L 4,90", ""),
            ("Pago Marille / Johannesbeer", "0,20Fl 3,90", ""),
            ("Lychee / Mango / Aloe vera", "0,30L 3,90 \u00b7 0,50L 5,90", ""),
            ("Apfelsaft / Orangensaft", "0,30L 3,60 \u00b7 0,50L 5,70", ""),
            ("Gespritzte mit Wasser/Soda", "0,30L 3,00 \u00b7 0,50L 4,20/4,50", ""),
            ("Calpis gespritzt", "0,50L 5,50/5,90", ""),
            ("Wiener Hochquellwasser", "0,50L 1,50", ""),
            ("Tonic Water", "0,20L 3,50", ""),
            ("Red Bull", "0,25L 4,00", ""),
        ],
    },
    {
        "title": "Hausgemachte Limonade",
        "chinese": "\u81ea\u5236\u51b0\u996e",
        "allergens": "",
        "items": [
            ("TanTan Limonade (Orange, Apfel, Lemonglass, Minze)", "0,50L 5,90", ""),
            ("GingerLimetten Limonade (0% Kalorien)", "0,50L 5,90", ""),
            ("Drachenfrucht Zitrone Limonade (0% Kalorien)", "0,50L 5,90", ""),
            ("PfirsichMaracuja Limonade", "0,50L 5,90", ""),
            ("GurkenLimetten Limonade", "0,50L 5,90", ""),
        ],
    },
    {
        "title": "Tee / Tea",
        "chinese": "\u8336",
        "allergens": "",
        "items": [
            ("OoLongCha \u4e4c\u9f99\u8336", "5,50", ""),
            ("RosenTee \u7384\u7470\u8336", "5,50", ""),
            ("AnJiBaiCha \u5b89\u5409\u767d\u8336 AnJi Weiss Tee", "5,50", ""),
            ("WuYuTai \u5434\u88d5\u6cf0\u8309\u8389\u82b1\u8336 Jasmine Tee", "5,50", ""),
            ("BaBaoCha \u516b\u5b9d\u8336 Achtsch\u00e4tze Tee", "5,50", ""),
            ("JianCha \u59dc\u8336 Ingwer Tee", "4,20", ""),
            ("Gr\u00fcner / Jasmin Tee", "4,20", ""),
            ("Schwarzer Tee / Fr\u00fcchte Tee", "4,20", ""),
        ],
    },
    {
        "title": "Schnaps / Spirits",
        "chinese": "\u70c8\u9152",
        "allergens": "A",
        "items": [
            ("LuZhouLaoJiao 100ml", "16,50", ""),
            ("MaoTai 2cl", "5,90", ""),
            ("Ginseng Schnaps 2cl", "5,50", ""),
            ("Bambus Schnaps 2cl", "4,90", ""),
            ("GaoLiangJiu 2cl", "4,90", ""),
            ("WuJiaPi 2cl", "4,90", ""),
            ("Barack 2cl", "4,50", ""),
            ("Martini 4cl", "4,90", ""),
            ("Campari-Soda/Orange", "5,20", ""),
            ("Wodka 2cl", "4,50", ""),
            ("Gin 4cl", "7,50", ""),
            ("Gin Tonic", "8,90", ""),
            ("Cognac 2cl", "5,90", ""),
            ("Whisky 2cl", "5,90", ""),
        ],
    },
    {
        "title": "Bier / Beer",
        "chinese": "\u5564\u9152",
        "allergens": "A O",
        "items": [
            ("G\u00f6sser Gold Fass", "0,30L 4,30 \u00b7 0,50L 5,00", ""),
            ("Radler", "0,30L 4,50 \u00b7 0,50L 5,30", ""),
            ("Tsingtao Beer", "0,33Fl 4,70", ""),
            ("Budweiser", "0,50Fl 5,20", ""),
            ("Weizenbier", "0,50Fl 5,20", ""),
            ("Dunkles Bier", "0,50Fl 5,20", ""),
            ("Alkoholfr. Bier", "0,50Fl 5,20", ""),
            ("Heineken", "0,33Fl 4,70", ""),
        ],
    },
    {
        "title": "Wein / Wine",
        "chinese": "\u9152",
        "allergens": "O",
        "items": [
            ("Haus Weisswein", "1/8 3,30 \u00b7 1/4 5,90", ""),
            ("Haus Rotwein", "1/8 3,40 \u00b7 1/4 6,20", ""),
            ("Spritzer Rot/Wei\u00df", "3,90", ""),
            ("Aperol Prosecco / Spritzer", "6,20", ""),
            ("Himbeer Spritzer", "6,20", ""),
            ("Hugo Spritzer", "6,20", ""),
            ("Pflaumenwein / Mandarinenwein warm", "6cl 4,20", ""),
            ("Sparkling Brut, Schlumberger", "39,90", ""),
            ("Sekt Hochriegel trocken", "28,90", ""),
            ("Sekt / Sekt-Orange", "Glas 5,50/5,00", ""),
        ],
    },
    {
        "title": "Kaffee / Coffee",
        "chinese": "\u5496\u5561",
        "allergens": "",
        "items": [
            ("Espresso kleiner / doppelter", "2,50 / 4,20", ""),
            ("Brauner kleiner / gro\u00dfer", "2,80 / 4,50", ""),
            ("Verl\u00e4ngerter ohne/mit Milch", "3,20 / 3,50", ""),
            ("Melange", "3,50", ""),
            ("Cappuccino", "3,70", ""),
            ("Cafe Latte", "4,50", ""),
        ],
    },
]


# ---------------------------------------------------------------------------
# Helper: find image or generate placeholder
# ---------------------------------------------------------------------------
def find_image(code: str, subdir: str = "") -> str | None:
    """Return relative path to image if exists, else None."""
    base = IMAGES_DIR / subdir if subdir else IMAGES_DIR
    if not base.is_dir():
        return None
    prefix = f"./images/{subdir}/" if subdir else "./images/"
    for ext in ("jpg", "jpeg", "webp", "png"):
        candidate = base / f"{code}.{ext}"
        if candidate.exists():
            return f"{prefix}{code}.{ext}"
    for f in base.iterdir():
        if f.stem.lower() == code.lower() and f.suffix.lower() in (".jpg", ".jpeg", ".webp", ".png"):
            return f"{prefix}{f.name}"
    return None


def make_placeholder_svg(code: str, name: str, chinese: str) -> str:
    """Generate a base64-encoded SVG placeholder."""
    prefix = code.rstrip("0123456789abcdefg").upper()
    if not prefix:
        prefix = code[0].upper()
    c1, c2 = GRADIENT_MAP.get(prefix, ("#c41e3a", "#8b0000"))

    display_text = html_mod.escape(chinese) if chinese else html_mod.escape(name)
    # Truncate for display
    if len(display_text) > 12:
        display_text = display_text[:12]

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="220" height="180" viewBox="0 0 220 180">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="{c2}" stop-opacity="0.95"/>
    </linearGradient>
  </defs>
  <rect width="220" height="180" fill="url(#g)" rx="6"/>
  <text x="110" y="75" text-anchor="middle" fill="rgba(255,255,255,0.25)" font-size="56" font-family="serif">{html_mod.escape(code)}</text>
  <text x="110" y="120" text-anchor="middle" fill="white" font-size="26" font-family="serif" opacity="0.9">{display_text}</text>
  <text x="110" y="148" text-anchor="middle" fill="rgba(255,255,255,0.6)" font-size="11" font-family="sans-serif">{html_mod.escape(name)}</text>
</svg>'''
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def image_tag(code: str, name: str, chinese: str, subdir: str = "") -> str:
    """Return <img> tag -- real image or placeholder."""
    real = find_image(code, subdir)
    if real:
        return f'<img src="{html_mod.escape(real)}" alt="{html_mod.escape(name)}" loading="lazy">'
    else:
        src = make_placeholder_svg(code, name, chinese)
        return f'<img src="{src}" alt="{html_mod.escape(name)}">'


# ---------------------------------------------------------------------------
# HTML rendering helpers
# ---------------------------------------------------------------------------
def render_allergens(allergen_str: str) -> str:
    """Render allergen badges."""
    if not allergen_str.strip():
        return ""
    codes = allergen_str.strip().split()
    badges = []
    for c in codes:
        c = c.strip()
        if c:
            tip = html_mod.escape(ALLERGEN_MAP.get(c, c))
            badges.append(f'<span class="allergen-badge" title="{tip}">{html_mod.escape(c)}</span>')
    return " ".join(badges)


def render_food_item(item: dict, subdir: str = "", category: str = "") -> str:
    """Render a single food item as an Instagram-style tile."""
    code = item["code"]
    name = item["name"]
    chinese = item["chinese"]
    english_name = item.get("english_name", "")
    price = item["price"]

    img = image_tag(code, name, chinese, subdir)
    # Build display name: show both English and Chinese if available
    display_name = english_name if english_name else name
    # Add Chinese subtitle if we have one and it's different
    chinese_line = ""
    if chinese:
        chinese_line = f'<span class="tile-chinese">{html_mod.escape(chinese)}</span>'

    cat_attr = f' data-category="{html_mod.escape(category)}"' if category else ""
    data_attrs = f' data-code="{html_mod.escape(code)}" data-name="{html_mod.escape(display_name)}" data-price="{html_mod.escape(price)}"'

    return f'''<div class="menu-tile"{cat_attr}{data_attrs} onclick="toggleSelect(this)">
  <div class="tile-image">{img}</div>
  <div class="tile-check"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#22c55e" stroke="#fff" stroke-width="1.5"/><path d="M7 12.5l3 3 7-7" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></div>
  <div class="tile-caption">
    <div class="tile-name-wrap">
      <span class="tile-name">{html_mod.escape(display_name)}</span>
      {chinese_line}
    </div>
    <span class="tile-price">\u20ac{html_mod.escape(price)}</span>
  </div>
</div>'''


def render_flat_grid(sections: list, subdir: str = "") -> str:
    """Render all food sections as one continuous Instagram-style grid."""
    parts = []
    parts.append('<div class="menu-grid">')
    for section in sections:
        cat_id = section["title"].lower().replace(" ", "-").replace("·", "").replace("  ", "-").strip("-")
        first = True
        for item in section["items"]:
            tile = render_food_item(item, subdir, cat_id)
            if first:
                # Mark the first item of each category as a scroll sentinel
                tile = tile.replace('class="menu-tile"', f'class="menu-tile" data-category-start="{html_mod.escape(cat_id)}"', 1)
                first = False
            parts.append(tile)
    parts.append('</div>')
    return "\n".join(parts)


def render_category_pills(sections: list, drink_sections: list = None) -> str:
    """Render floating category pill navigation."""
    pills = ['<button class="cat-pill cat-pill--active" data-cat="all">All</button>']
    for section in sections:
        cat_id = section["title"].lower().replace(" ", "-").replace("·", "").replace("  ", "-").strip("-")
        # Short label
        label = section["title"].split("·")[-1].strip() if "·" in section["title"] else section["title"]
        pills.append(f'<button class="cat-pill" data-cat="{html_mod.escape(cat_id)}">{html_mod.escape(label)}</button>')
    # Add a Drinks pill if drink sections exist
    if drink_sections:
        pills.append('<button class="cat-pill" data-cat="drinks">Drinks</button>')
    return '<div class="cat-nav">\n' + "\n".join(pills) + '\n</div>'


def _drink_code(section_title: str, idx: int) -> str:
    """Generate a stable code for a drink item."""
    prefix = section_title[:3].upper().replace(" ", "")
    return f"DR-{prefix}{idx}"


def render_drink_section(section: dict) -> str:
    """Render a drink section as a simple table with selectable rows."""
    title = section["title"]
    chinese = section["chinese"]
    allergens = section.get("allergens", "")

    parts = []
    parts.append('<div class="menu-section drink-section">')
    parts.append(f'  <div class="section-header">')
    parts.append(f'    <span class="section-chinese">{html_mod.escape(chinese)}</span>')
    title_html = html_mod.escape(title)
    if allergens:
        title_html += f' <span class="section-allergen-note">{render_allergens(allergens)}</span>'
    parts.append(f'    <h2 class="section-title">{title_html}</h2>')
    parts.append(f'  </div>')
    parts.append('  <div class="drink-list">')

    for idx, item in enumerate(section["items"], 1):
        name_str, price_str, detail = item
        code = _drink_code(title, idx)
        # Extract first numeric price for selection
        first_price = price_str.split("·")[0].strip()
        data_attrs = f'data-code="{html_mod.escape(code)}" data-name="{html_mod.escape(name_str)}" data-price="{html_mod.escape(first_price)}"'
        parts.append(f'    <div class="drink-row" {data_attrs} onclick="toggleSelect(this)">')
        parts.append(f'      <span class="drink-name">{html_mod.escape(name_str)}</span>')
        if detail:
            parts.append(f'      <span class="drink-detail">{html_mod.escape(detail)}</span>')
        parts.append(f'      <span class="drink-price">{html_mod.escape(price_str)}</span>')
        parts.append(f'      <span class="drink-check"><svg viewBox="0 0 20 20" width="16" height="16"><circle cx="10" cy="10" r="9" fill="#22c55e" stroke="#fff" stroke-width="1"/><path d="M6 10.5l2.5 2.5 5.5-5.5" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg></span>')
        parts.append('    </div>')

    parts.append('  </div>')
    parts.append('</div>')
    return "\n".join(parts)


def render_allergen_legend() -> str:
    """Render the allergen legend table."""
    rows = []
    for code in ("A", "B", "C", "D", "E", "F", "G", "H", "L", "M", "N", "O", "P", "R"):
        desc = ALLERGEN_MAP.get(code, "")
        rows.append(f'<div class="legend-item"><span class="allergen-badge">{code}</span> {html_mod.escape(desc)}</div>')
    return '<div class="allergen-legend">\n' + "\n".join(rows) + "\n</div>"


# ---------------------------------------------------------------------------
# Full HTML assembly
# ---------------------------------------------------------------------------
def build_html() -> str:
    """Build the complete HTML document with Menu + Selection tabs."""

    # Category pill navigation (includes Drinks pill)
    cat_pills = render_category_pills(FOOD_SECTIONS, DRINK_SECTIONS)

    # Render flat grid (nano images only)
    food_grid = render_flat_grid(FOOD_SECTIONS, "nano")

    # Render all drink sections
    drink_html = "\n".join(render_drink_section(s) for s in DRINK_SECTIONS)

    # Allergen legend
    legend = render_allergen_legend()

    return f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>TANTAN \u2013 Chinese Fine Dining \u00b7 Vienna</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; -webkit-tap-highlight-color: transparent; }}
body {{
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: #0a0a0a;
  color: #e0d8d0;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}}

/* ---- Header ---- */
.site-header {{
  background: #0a0a0a;
  text-align: center;
  padding: 14px 16px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}}
.header-brand {{
  font-weight: 700;
  font-size: 1.6rem;
  letter-spacing: 0.22em;
  color: #fff;
}}
.header-tagline {{
  font-weight: 300;
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  color: rgba(255,255,255,0.4);
  margin-top: 2px;
}}

/* ---- Tab Bar ---- */
.tab-bar {{
  display: flex;
  gap: 0;
  margin-top: 12px;
  border-bottom: 2px solid #222;
}}
.tab {{
  flex: 1;
  background: none;
  border: none;
  color: #666;
  font-family: inherit;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 10px 0;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
}}
.tab.active {{
  color: #c41e3a;
  border-bottom-color: #c41e3a;
}}
.tab-content {{
  display: none;
}}
.tab-content.active {{
  display: block;
}}

/* ---- Category Pill Nav ---- */
.cat-nav {{
  background: #0a0a0a;
  padding: 6px 8px 8px;
  overflow-x: auto;
  scrollbar-width: none;
  display: flex;
  gap: 6px;
  -webkit-overflow-scrolling: touch;
  border-bottom: 1px solid #1a1a1a;
}}
.cat-nav::-webkit-scrollbar {{ display: none; }}
.cat-pill {{
  padding: 5px 14px;
  border-radius: 20px;
  border: 1.5px solid #333;
  background: transparent;
  font-family: inherit;
  font-size: 0.7rem;
  font-weight: 500;
  color: #888;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}}
.cat-pill--active {{
  background: #c41e3a;
  color: #fff;
  border-color: #c41e3a;
}}

/* ---- Instagram Grid ---- */
.menu-grid {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 3px;
}}

/* ---- Tile ---- */
.menu-tile {{
  position: relative;
  overflow: hidden;
  aspect-ratio: 9 / 16;
}}
.tile-image {{
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #111;
}}
.tile-image img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
}}
.menu-tile:hover .tile-image img {{
  transform: scale(1.05);
}}
/* Gradient overlay at bottom for text legibility */
.menu-tile::after {{
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 45%;
  background: linear-gradient(transparent, rgba(0,0,0,0.7));
  pointer-events: none;
}}
.tile-caption {{
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding: 8px 10px;
  gap: 6px;
}}
.tile-name-wrap {{
  flex: 1;
  min-width: 0;
}}
.tile-name {{
  display: block;
  font-weight: 600;
  font-size: 0.75rem;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 0 1px 3px rgba(0,0,0,0.5);
}}
.tile-chinese {{
  display: block;
  font-size: 0.65rem;
  color: rgba(255,255,255,0.65);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 0 1px 3px rgba(0,0,0,0.5);
  margin-top: 1px;
}}
.tile-price {{
  font-weight: 700;
  font-size: 0.78rem;
  color: #fff;
  white-space: nowrap;
  flex-shrink: 0;
  text-shadow: 0 1px 3px rgba(0,0,0,0.5);
  align-self: flex-end;
}}

/* ---- Selection Checkmark ---- */
.tile-check {{
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  z-index: 3;
  opacity: 0;
  transform: scale(0.5);
  transition: opacity 0.2s, transform 0.2s;
  pointer-events: none;
  filter: drop-shadow(0 1px 3px rgba(0,0,0,0.4));
}}
.menu-tile.selected .tile-check {{
  opacity: 1;
  transform: scale(1);
}}
.menu-tile {{
  cursor: pointer;
  -webkit-user-select: none;
  user-select: none;
}}
.menu-tile.selected {{
  outline: 2px solid #22c55e;
  outline-offset: -2px;
}}

/* ---- Receipt / Selection Tab ---- */
.receipt {{
  max-width: 420px;
  margin: 20px auto;
  padding: 24px 20px;
  background: #111;
  border: 1px dashed #333;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}}
.receipt-header {{
  text-align: center;
  padding-bottom: 12px;
  border-bottom: 1px dashed #333;
  margin-bottom: 12px;
}}
.receipt-header h3 {{
  font-size: 1.1rem;
  color: #fff;
  letter-spacing: 0.15em;
  font-weight: 700;
}}
.receipt-header p {{
  font-size: 0.65rem;
  color: #555;
  margin-top: 4px;
}}
.receipt-empty {{
  text-align: center;
  padding: 40px 0;
  color: #444;
  font-size: 0.8rem;
}}
.receipt-items {{
  list-style: none;
}}
.receipt-item {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px dotted #222;
  gap: 8px;
}}
.receipt-item:last-child {{ border-bottom: none; }}
.receipt-item-left {{
  flex: 1;
  min-width: 0;
}}
.receipt-item-name {{
  display: block;
  font-size: 0.75rem;
  color: #ccc;
}}
.receipt-item-chinese {{
  display: block;
  font-size: 0.6rem;
  color: #555;
  margin-top: 1px;
}}
.receipt-item-right {{
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}}
.qty-controls {{
  display: flex;
  align-items: center;
  gap: 0;
  border: 1px solid #333;
  border-radius: 6px;
  overflow: hidden;
}}
.qty-btn {{
  width: 28px;
  height: 28px;
  background: #1a1a1a;
  border: none;
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}}
.qty-btn:active {{ background: #333; }}
.qty-num {{
  width: 28px;
  text-align: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
  background: #111;
}}
.receipt-item-price {{
  font-size: 0.78rem;
  color: #ccc;
  white-space: nowrap;
  text-align: right;
  min-width: 55px;
}}
.clear-btn {{
  display: block;
  width: 100%;
  margin-top: 12px;
  padding: 10px;
  background: none;
  border: 1px solid #333;
  border-radius: 8px;
  color: #666;
  font-family: inherit;
  font-size: 0.72rem;
  cursor: pointer;
  transition: all 0.15s;
}}
.clear-btn:active {{ background: #1a1a1a; color: #c41e3a; border-color: #c41e3a; }}
.receipt-total {{
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding: 12px 0 4px;
  margin-top: 8px;
  border-top: 2px solid #333;
  font-weight: 700;
}}
.receipt-total-label {{
  font-size: 0.85rem;
  color: #fff;
}}
.receipt-total-amount {{
  font-size: 1rem;
  color: #22c55e;
}}
.receipt-count {{
  text-align: center;
  font-size: 0.65rem;
  color: #555;
  margin-top: 8px;
}}
.selection-badge {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  background: #22c55e;
  color: #000;
  font-size: 0.6rem;
  font-weight: 700;
  margin-left: 6px;
  padding: 0 5px;
  vertical-align: middle;
}}

/* ---- Container (for drinks/allergens below grid) ---- */
.container {{
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
  padding: 20px 8px 80px;
}}

/* ---- Section ---- */
.menu-section {{
  margin-bottom: 28px;
}}
.section-header {{
  text-align: center;
  padding: 16px 8px 8px;
}}
.section-chinese {{
  display: block;
  font-size: 1.1rem;
  color: #c41e3a;
  letter-spacing: 0.1em;
}}
.section-title {{
  font-weight: 600;
  font-size: 0.95rem;
  color: #ccc;
  letter-spacing: 0.02em;
}}
.section-subtitle {{
  font-weight: 400;
  color: #666;
  font-size: 0.8em;
}}
.section-allergen-note {{
  display: inline-flex;
  gap: 3px;
  margin-left: 6px;
  vertical-align: middle;
}}
.section-note {{
  text-align: center;
  font-size: 0.68rem;
  color: #666;
  margin-bottom: 4px;
  font-style: italic;
}}
.note-secondary {{
  color: #a08060;
}}

/* ---- Allergen badge (used in legend + drinks) ---- */
.allergen-badge {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  font-size: 0.55rem;
  font-weight: 600;
  border-radius: 50%;
  background: rgba(255,255,255,0.07);
  color: #888;
  border: 1px solid rgba(255,255,255,0.1);
  flex-shrink: 0;
}}

/* ---- Drinks ---- */
.drink-section .drink-list {{
  background: #141414;
  border-radius: 12px;
  overflow: hidden;
}}
.drink-row {{
  display: flex;
  align-items: baseline;
  padding: 7px 12px;
  gap: 6px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
}}
.drink-row:last-child {{ border-bottom: none; }}
.drink-row {{ cursor: pointer; transition: background 0.15s; }}
.drink-row:active {{ background: rgba(34,197,94,0.08); }}
.drink-row.selected {{ background: rgba(34,197,94,0.1); }}
.drink-check {{
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
}}
.drink-row.selected .drink-check {{ opacity: 1; }}
.drink-name {{
  flex: 1;
  font-size: 0.74rem;
  font-weight: 500;
  color: #bbb;
  min-width: 0;
}}
.drink-detail {{
  font-size: 0.62rem;
  color: #555;
  white-space: nowrap;
}}
.drink-price {{
  font-weight: 600;
  font-size: 0.74rem;
  color: #c41e3a;
  white-space: nowrap;
  text-align: right;
  min-width: 70px;
}}

/* ---- Allergen Legend ---- */
.allergen-legend {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px 12px;
  background: #141414;
  border-radius: 12px;
  padding: 14px;
  margin-top: 6px;
}}
.legend-item {{
  font-size: 0.65rem;
  color: #777;
  display: flex;
  align-items: center;
  gap: 5px;
}}

/* ---- Footer ---- */
.site-footer {{
  text-align: center;
  padding: 20px 16px 40px;
  font-size: 0.65rem;
  color: #444;
  line-height: 1.8;
}}

/* ---- Print ---- */
@media print {{
  body {{ background: #fff; color: #222; }}
  .site-header {{ background: #222 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; position: static; }}
  .tile-image img {{ border-radius: 8px; }}
  .tile-name {{ color: #222; }}
  .drink-section .drink-list {{ background: #f5f5f5; }}
  .drink-name {{ color: #222; }}
  .allergen-legend {{ background: #f5f5f5; }}
  .legend-item {{ color: #555; }}
}}
</style>
</head>
<body>

<header class="site-header">
  <div class="header-brand">TANTAN</div>
  <div class="header-tagline">Chinese Fine Dining &middot; Vienna</div>
  <div class="tab-bar">
    <button class="tab active" data-tab="menu">Menu</button>
    <button class="tab" data-tab="selection">Selection <span id="sel-badge" class="selection-badge" style="display:none">0</span></button>
  </div>
  {cat_pills}
</header>

<div id="tab-menu" class="tab-content active">
{food_grid}

<div class="container">
<div id="drinks-anchor"></div>
{drink_html}

<div class="menu-section">
  <div class="section-header">
    <span class="section-chinese">\u8fc7\u654f\u539f</span>
    <h2 class="section-title">Allergene / Allergens</h2>
  </div>
  {legend}
</div>
</div>
</div>

<div id="tab-selection" class="tab-content">
  <div class="receipt" id="receipt">
    <div class="receipt-header">
      <h3>TANTAN</h3>
      <p>Chinese Fine Dining &middot; Vienna</p>
      <p>Your Selection</p>
    </div>
    <div id="receipt-body">
      <p class="receipt-empty">Tap items on the menu to add them here</p>
    </div>
  </div>
</div>

<footer class="site-footer">
  <div>Alle Speisen auch zum Mitnehmen &mdash; All dishes also for takeaway</div>
  <div>Druckfehler und Preis\u00e4nderung vorbehalten</div>
  <div style="margin-top:6px;">&copy; TANTAN Chinese Fine Dining &middot; Wien</div>
</footer>

<script>
// ---- Tab switching ----
document.querySelectorAll('.tab').forEach(btn => {{
  btn.addEventListener('click', () => {{
    document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
    // Show/hide category pills based on active tab
    const catNav = document.querySelector('.cat-nav');
    if (catNav) catNav.style.display = btn.dataset.tab === 'menu' ? 'flex' : 'none';
    window.scrollTo(0, 0);
  }});
}});

// ---- Category pill navigation ----
document.querySelectorAll('.cat-pill').forEach(pill => {{
  pill.addEventListener('click', () => {{
    document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('cat-pill--active'));
    pill.classList.add('cat-pill--active');
    const cat = pill.dataset.cat;
    if (cat === 'all') {{
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
      return;
    }}
    // Handle drinks pill specially (scroll to drinks anchor)
    if (cat === 'drinks') {{
      const anchor = document.getElementById('drinks-anchor');
      if (anchor) {{
        const hdrH = document.querySelector('.site-header').offsetHeight;
        const y = anchor.getBoundingClientRect().top + window.scrollY - hdrH - 4;
        window.scrollTo({{ top: y, behavior: 'smooth' }});
      }}
      return;
    }}
    const sentinel = document.querySelector('#tab-menu [data-category-start="' + cat + '"]');
    if (sentinel) {{
      const hdrH = document.querySelector('.site-header').offsetHeight;
      const y = sentinel.getBoundingClientRect().top + window.scrollY - hdrH - 4;
      window.scrollTo({{ top: y, behavior: 'smooth' }});
    }}
  }});
}});

// ---- Auto-highlight pill on scroll ----
const catNav = document.querySelector('.cat-nav');
if (catNav) {{
  const observer = new IntersectionObserver((entries) => {{
    entries.forEach(entry => {{
      if (entry.isIntersecting) {{
        const cat = entry.target.getAttribute('data-category-start');
        if (cat) {{
          document.querySelectorAll('.cat-pill').forEach(p => p.classList.remove('cat-pill--active'));
          const pill = document.querySelector('.cat-pill[data-cat="' + cat + '"]');
          if (pill) {{
            pill.classList.add('cat-pill--active');
            pill.scrollIntoView({{ behavior: 'smooth', block: 'nearest', inline: 'center' }});
          }}
        }}
      }}
    }});
  }}, {{ rootMargin: '-' + catNav.offsetHeight + 'px 0px -80% 0px', threshold: 0 }});
  document.querySelectorAll('[data-category-start]').forEach(el => observer.observe(el));
}}

// ---- Selection / Receipt system ----
const selected = new Map(); // code -> {{name, price, chinese, qty}}

function toggleSelect(el) {{
  const code = el.dataset.code;
  const name = el.dataset.name;
  const price = el.dataset.price;
  const chEl = el.querySelector('.tile-chinese');
  const chinese = chEl ? chEl.textContent : '';

  if (selected.has(code)) {{
    selected.delete(code);
    el.classList.remove('selected');
  }} else {{
    selected.set(code, {{ name, price, chinese, qty: 1 }});
    el.classList.add('selected');
  }}
  updateReceipt();
}}

function changeQty(code, delta) {{
  const item = selected.get(code);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) {{
    selected.delete(code);
    // Remove selected class from menu tile/drink row
    document.querySelectorAll('[data-code="' + code + '"]').forEach(el => el.classList.remove('selected'));
  }}
  updateReceipt();
}}

function clearAll() {{
  selected.clear();
  document.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
  updateReceipt();
}}

function parsePrice(p) {{
  // Handle prices like "0,30L 2,50" -> extract last number
  const matches = p.match(/(\\d+[,.]\\d+)/g);
  if (matches) return parseFloat(matches[matches.length - 1].replace(',', '.'));
  return 0;
}}

function updateReceipt() {{
  const badge = document.getElementById('sel-badge');
  const body = document.getElementById('receipt-body');

  // Count total items (sum of quantities)
  let totalItems = 0;
  selected.forEach(item => totalItems += item.qty);

  // Update badge
  if (totalItems > 0) {{
    badge.textContent = totalItems;
    badge.style.display = 'inline-flex';
  }} else {{
    badge.style.display = 'none';
  }}

  // Build receipt
  if (selected.size === 0) {{
    body.innerHTML = '<p class="receipt-empty">Tap items on the menu to add them here</p>';
    return;
  }}

  let total = 0;
  let html = '<ul class="receipt-items">';
  selected.forEach((item, code) => {{
    const unitPrice = parsePrice(item.price);
    const lineTotal = unitPrice * item.qty;
    total += lineTotal;
    const chineseSpan = item.chinese ? '<span class="receipt-item-chinese">' + item.chinese + '</span>' : '';
    html += '<li class="receipt-item">';
    html += '<div class="receipt-item-left">';
    html += '<span class="receipt-item-name">' + item.name + '</span>';
    if (chineseSpan) html += chineseSpan;
    html += '</div>';
    html += '<div class="receipt-item-right">';
    html += '<div class="qty-controls">';
    html += '<button class="qty-btn" onclick="event.stopPropagation();changeQty(\\'' + code + '\\',-1)">−</button>';
    html += '<span class="qty-num">' + item.qty + '</span>';
    html += '<button class="qty-btn" onclick="event.stopPropagation();changeQty(\\'' + code + '\\',1)">+</button>';
    html += '</div>';
    html += '<span class="receipt-item-price">&euro;' + lineTotal.toFixed(2).replace('.', ',') + '</span>';
    html += '</div>';
    html += '</li>';
  }});
  html += '</ul>';
  html += '<div class="receipt-total">';
  html += '<span class="receipt-total-label">TOTAL</span>';
  html += '<span class="receipt-total-amount">&euro;' + total.toFixed(2).replace('.', ',') + '</span>';
  html += '</div>';
  html += '<p class="receipt-count">' + totalItems + ' item' + (totalItems !== 1 ? 's' : '') + '</p>';
  html += '<button class="clear-btn" onclick="clearAll()">Clear All</button>';

  body.innerHTML = html;
}}
</script>

</body>
</html>'''


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    html_content = build_html()
    OUTPUT_FILE.write_text(html_content, encoding="utf-8")
    print(f"Menu generated: {OUTPUT_FILE}")
    print(f"Size: {OUTPUT_FILE.stat().st_size:,} bytes")

    # Auto-open in default browser
    try:
        url = OUTPUT_FILE.as_uri()
    except AttributeError:
        # Fallback for older Python
        url = "file:///" + str(OUTPUT_FILE).replace("\\", "/")
    webbrowser.open(url)
    print("Opened in browser.")


if __name__ == "__main__":
    main()
