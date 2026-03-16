"""
Process raw Instagram data into clean CSVs.

Inputs:
  data/raw/instagram_profiles.json
  data/raw/instagram_posts.json

Outputs:
  data/processed/instagram_posts_clean.csv
  (profile metrics are returned for use by merge_coaches.py)
"""

import json
import os
import re
import pandas as pd

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

# --- CTA keyword patterns ---
CTA_PATTERNS = {
    "whatsapp": [r"whatsapp", r"wa\.me", r"wa link", r"escribeme"],
    "linktree": [r"linktree", r"linktr\.ee", r"link\.bio"],
    "direct_website": [r"https?://(?!instagram|linktr|wa\.me)", r"www\."],
    "email": [r"[\w\.-]+@[\w\.-]+\.\w+"],
}

CONTENT_KEYWORDS = {
    "promotion": ["oferta", "promo", "precio", "descuento", "disponible", "cupo", "inscripcion", "inscripción", "venta"],
    "testimonial": ["transformacion", "transformación", "resultado", "testimonio", "cliente", "logro", "antes", "despues", "después"],
    "nutrition": ["nutricion", "nutrición", "dieta", "comida", "receta", "proteina", "proteína", "calorias", "calorías", "macro"],
    "workout": ["entreno", "workout", "ejercicio", "rutina", "gym", "peso", "series", "repeticiones", "cardio", "fuerza"],
    "lifestyle": ["vida", "motivacion", "motivación", "mentalidad", "mindset", "habito", "hábito", "bienestar"],
}


def _parse_followers(val) -> int:
    """Handle string values like '10.2k', '1.5M', or plain integers."""
    if val is None:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    val = str(val).lower().replace(",", "").strip()
    if "k" in val:
        return int(float(val.replace("k", "")) * 1000)
    if "m" in val:
        return int(float(val.replace("m", "")) * 1_000_000)
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0


def _detect_cta(text: str) -> str:
    if not text:
        return "none"
    text = text.lower()
    for cta_type, patterns in CTA_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text):
                return cta_type
    return "none"


def _classify_content(caption: str) -> str:
    if not caption:
        return "lifestyle"
    caption = caption.lower()
    for category, keywords in CONTENT_KEYWORDS.items():
        if any(kw in caption for kw in keywords):
            return category
    return "lifestyle"


def process_profiles(profiles: list) -> pd.DataFrame:
    rows = []
    for p in profiles:
        username = (
            p.get("username")
            or p.get("inputUrl", "").split("/")[-2]
            or "unknown"
        )
        followers = _parse_followers(
            p.get("followersCount") or p.get("followers") or p.get("edge_followed_by", {}).get("count", 0)
        )
        bio = p.get("biography") or p.get("bio") or ""
        rows.append({
            "coach_username": username,
            "full_name": p.get("fullName") or p.get("full_name") or p.get("name") or username,
            "ig_followers": followers,
            "ig_following": _parse_followers(p.get("followsCount") or p.get("following") or 0),
            "ig_posts_count": _parse_followers(p.get("postsCount") or p.get("mediaCount") or 0),
            "ig_verified": bool(p.get("verified") or p.get("is_verified", False)),
            "ig_bio": bio,
            "ig_bio_cta_type": _detect_cta(bio),
            "ig_has_external_link": bool(p.get("externalUrl") or p.get("website") or p.get("external_url")),
            "ig_external_url": p.get("externalUrl") or p.get("website") or p.get("external_url") or "",
        })
    return pd.DataFrame(rows)


def process_posts(posts: list, profiles_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for post in posts:
        username = (
            post.get("ownerUsername")
            or post.get("username")
            or post.get("owner", {}).get("username", "unknown")
        )
        likes = int(post.get("likesCount") or post.get("likes") or post.get("edge_media_preview_like", {}).get("count", 0) or 0)
        comments = int(post.get("commentsCount") or post.get("comments") or post.get("edge_media_to_comment", {}).get("count", 0) or 0)
        caption = post.get("caption") or post.get("accessibility_caption") or ""
        post_type = post.get("type") or post.get("product_type") or "post"
        if post.get("isVideo") or post.get("is_video"):
            post_type = "reel"

        rows.append({
            "coach_username": username,
            "post_shortcode": post.get("shortCode") or post.get("shortcode") or post.get("id") or "",
            "post_type": post_type,
            "likes": likes,
            "comments": comments,
            "timestamp": post.get("timestamp") or post.get("taken_at_timestamp") or "",
            "caption_length": len(caption),
            "has_cta": any(
                kw in caption.lower()
                for kw in ["link", "whatsapp", "dm", "agenda", "reserva", "descarga", "gratis", "free", "precio"]
            ),
            "content_category": _classify_content(caption),
            "is_reel": post_type in ("reel", "video"),
        })

    posts_df = pd.DataFrame(rows)

    # Compute per-coach engagement averages and merge back
    if not posts_df.empty and not profiles_df.empty:
        agg = posts_df.groupby("coach_username").agg(
            avg_likes=("likes", "mean"),
            avg_comments=("comments", "mean"),
            post_count_scraped=("likes", "count"),
        ).reset_index()

        profiles_enriched = profiles_df.merge(agg, on="coach_username", how="left")
        profiles_enriched["ig_avg_likes"] = profiles_enriched["avg_likes"].fillna(0)
        profiles_enriched["ig_avg_comments"] = profiles_enriched["avg_comments"].fillna(0)
        profiles_enriched["ig_engagement_rate"] = profiles_enriched.apply(
            lambda r: round(
                (r["ig_avg_likes"] + r["ig_avg_comments"]) / r["ig_followers"] * 100, 2
            ) if r["ig_followers"] > 0 else 0.0,
            axis=1,
        )
    else:
        profiles_enriched = profiles_df.copy()
        for col in ["ig_avg_likes", "ig_avg_comments", "ig_engagement_rate"]:
            profiles_enriched[col] = 0.0

    return posts_df, profiles_enriched


def run() -> pd.DataFrame:
    profiles_path = os.path.join(RAW_DIR, "instagram_profiles.json")
    posts_path = os.path.join(RAW_DIR, "instagram_posts.json")

    if not os.path.exists(profiles_path):
        print("[instagram_processor] No instagram_profiles.json found. Run collection first.")
        return pd.DataFrame()

    with open(profiles_path, encoding="utf-8") as f:
        profiles_raw = json.load(f)

    posts_raw = []
    if os.path.exists(posts_path):
        with open(posts_path, encoding="utf-8") as f:
            posts_raw = json.load(f)

    profiles_df = process_profiles(profiles_raw)
    posts_df, profiles_enriched = process_posts(posts_raw, profiles_df)

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    posts_out = os.path.join(PROCESSED_DIR, "instagram_posts_clean.csv")
    posts_df.to_csv(posts_out, index=False)
    print(f"[instagram_processor] Saved {len(posts_df)} posts -> {posts_out}")

    return profiles_enriched


if __name__ == "__main__":
    df = run()
    print(df[["coach_username", "ig_followers", "ig_engagement_rate"]].to_string())
