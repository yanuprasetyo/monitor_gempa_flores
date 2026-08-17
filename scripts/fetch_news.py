#!/usr/bin/env python3
"""
Ambil berita tentang Gempa Flores/Maumere 2026 dari Google News RSS,
kelompokkan menurut fase penanganan bencana, dan simpan ke data/news.json.

Tidak butuh instalasi library tambahan (hanya modul bawaan Python),
supaya bisa langsung dijalankan oleh GitHub Actions tanpa setup rumit.
"""

import json
import os
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# ----------------------------------------------------------------------
# PENGATURAN — ubah bagian ini kalau ingin menyesuaikan cakupan pemantauan
# ----------------------------------------------------------------------

# Tanggal kejadian gempa (untuk hitung "hari ke-N pascabencana")
DISASTER_DATE = datetime(2026, 8, 15, tzinfo=timezone.utc)

# Kata kunci pencarian di Google News (masing-masing jadi satu query terpisah)
SEARCH_QUERIES = [
    "gempa Flores",
    "gempa Maumere",
    "gempa Sikka",
    "gempa Nagekeo",
    "gempa NTT 2026",
]

# Wilayah yang relevan (dipakai untuk menyaring berita yang benar-benar
# tentang Flores/Maumere/Sikka/Nagekeo, bukan gempa di daerah lain)
REGION_KEYWORDS = [
    "flores", "maumere", "sikka", "nagekeo", "mbay", "ende", "ngada",
    "ntt", "nusa tenggara timur",
]

# Kategori/fase penanganan bencana. Urutan menentukan prioritas ketika
# satu judul berita cocok dengan lebih dari satu kategori.
CATEGORIES = [
    {
        "id": "korban_kerusakan",
        "label": "Korban & Kerusakan",
        "keywords": [
            "korban", "tewas", "meninggal dunia", "meninggal", "luka-luka",
            "luka berat", "rusak", "roboh", "runtuh", "ambruk", "hancur",
            "reruntuhan", "hilang",
        ],
    },
    {
        "id": "tanggap_darurat",
        "label": "Tanggap Darurat & Evakuasi",
        "keywords": [
            "evakuasi", "mengungsi", "pengungsi", "pengungsian", "tanggap darurat",
            "sar ", "basarnas", "posko", "tenda darurat", "peringatan dini",
            "tsunami", "siaga", "dievakuasi", "penyelamatan",
        ],
    },
    {
        "id": "rehab_rekon",
        "label": "Rehabilitasi & Rekonstruksi",
        "keywords": [
            "rehabilitasi", "rekonstruksi", "rehab-rekon", "rehab rekon",
            "pembangunan kembali", "perbaikan infrastruktur", "huntara",
            "hunian sementara", "renduk", "rencana induk",
        ],
    },
    {
        "id": "pemulihan_bansos",
        "label": "Pemulihan & Bantuan Sosial",
        "keywords": [
            "bantuan sosial", "bansos", "logistik", "sembako", "donasi",
            "dana tunggu hunian", "dth", "bantuan logistik", "dapur umum",
            "pemulihan ekonomi", "trauma healing",
        ],
    },
    {
        "id": "gempa_umum",
        "label": "Gempa & Gempa Susulan (Umum)",
        "keywords": [
            "gempa susulan", "magnitudo", "guncang", "bmkg", "sesar",
            "gempa bumi", "kekuatan gempa", "episentrum", "kedalaman",
        ],
    },
]

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "news.json")
USER_AGENT = "Mozilla/5.0 (compatible; MonitorGempaFlores/1.0; +https://github.com/)"


def fetch_rss(query: str) -> bytes:
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
        "q": query,
        "hl": "id",
        "gl": "ID",
        "ceid": "ID:id",
    })
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def categorize(title: str) -> str:
    t = title.lower()
    for cat in CATEGORIES:
        for kw in cat["keywords"]:
            if kw in t:
                return cat["id"]
    return "gempa_umum"


def is_relevant(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in REGION_KEYWORDS)


def clean_source(title: str, source: str) -> tuple:
    """Google News sering menempel nama sumber di akhir judul (' - Nama Media')."""
    if source:
        return title, source
    if " - " in title:
        head, tail = title.rsplit(" - ", 1)
        return head.strip(), tail.strip()
    return title, "Tidak diketahui"


def parse_items(xml_bytes: bytes):
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.findall("./channel/item"):
        title_raw = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date_raw = (item.findtext("pubDate") or "").strip()
        source_el = item.find("source")
        source_raw = (source_el.text or "").strip() if source_el is not None else ""

        title, source = clean_source(title_raw, source_raw)

        try:
            pub_dt = parsedate_to_datetime(pub_date_raw)
            if pub_dt.tzinfo is None:
                pub_dt = pub_dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue

        items.append({
            "title": title,
            "link": link,
            "source": source or "Tidak diketahui",
            "published": pub_dt.isoformat(),
        })
    return items


def main():
    all_items = {}  # dedup by normalized title

    for q in SEARCH_QUERIES:
        try:
            xml_bytes = fetch_rss(q)
            items = parse_items(xml_bytes)
        except Exception as e:
            print(f"Gagal mengambil query '{q}': {e}")
            continue

        for it in items:
            if not is_relevant(it["title"]):
                continue
            key = re.sub(r"\s+", " ", it["title"].lower()).strip()
            if key not in all_items:
                it["category"] = categorize(it["title"])
                all_items[key] = it

    articles = sorted(all_items.values(), key=lambda x: x["published"], reverse=True)

    # Muat data lama (kalau ada) supaya berita lama tetap tersimpan meski
    # sudah tidak muncul lagi di hasil pencarian RSS terbaru.
    existing = []
    if os.path.exists(OUTPUT_PATH):
        try:
            with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f).get("articles", [])
        except Exception:
            existing = []

    merged = {re.sub(r"\s+", " ", a["title"].lower()).strip(): a for a in existing}
    for a in articles:
        key = re.sub(r"\s+", " ", a["title"].lower()).strip()
        merged[key] = a  # data baru menimpa data lama untuk judul yang sama

    final_articles = sorted(merged.values(), key=lambda x: x["published"], reverse=True)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "disaster_date": DISASTER_DATE.isoformat(),
        "categories": [{"id": c["id"], "label": c["label"]} for c in CATEGORIES],
        "total_articles": len(final_articles),
        "articles": final_articles,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Selesai. {len(final_articles)} berita tersimpan di {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
