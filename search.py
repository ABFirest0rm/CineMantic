import json, os, re, sqlite3, time, random
import numpy as np
import faiss
from mistralai import Mistral
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
from mistralai import Mistral

# Always load from project root (where app.py lives)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise RuntimeError("⚠️ Missing MISTRAL_API_KEY in .env")


client = Mistral(api_key=api_key)

# Load environment variables
load_dotenv()

# ---------- constants ----------
INDEX_DIR = "faiss_indices"
EMBED_MODEL = "mistral-embed"

# Load API key
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise RuntimeError("⚠️ Missing MISTRAL_API_KEY in .env")

client = Mistral(api_key=MISTRAL_API_KEY)

with open("few_shot_prompt.txt", "r") as f:
    FEW_SHOT_PROMPT = f.read()


# ---------- utilities ----------
def safe_chat_call(messages, model="mistral-small-latest", retries=5):
    for attempt in range(retries):
        try:
            return client.chat.complete(model=model, messages=messages)
        except Exception as e:
            if "429" in str(e):
                wait = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait)
                continue
            raise
    raise RuntimeError("Failed after retries")

def _clean_json_text(text: str) -> str:
    return re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE)

def _normalize_list(values):
    if not values: return ""
    if isinstance(values, str):
        try: values = json.loads(values)
        except: values = [values]
    values = [str(v).strip().lower() for v in values if v]
    values = [v for v in values if v not in {"horror", "thriller"}]  # skip generic
    return ", ".join(sorted(set(values))) if values else ""

def _load_index(name):
    return faiss.read_index(os.path.join(INDEX_DIR, f"{name}.faiss"))

def _embed_text(text: str) -> np.ndarray | None:
    text = (text or "").strip()
    if not text:
        return None
    resp = client.embeddings.create(model=EMBED_MODEL, inputs=text)
    return np.array(resp.data[0].embedding, dtype=np.float32)

# ---------- 1) parse query ----------
def parse_query_with_llm(user_query: str) -> dict:
    result = safe_chat_call(
        messages=[
            {"role": "system", "content": FEW_SHOT_PROMPT},
            {"role": "user", "content": user_query}
        ]
    )
    raw = result.choices[0].message.content
    txt = _clean_json_text(raw)
    try:
        parsed = json.loads(txt)
    except Exception:
        parsed = {"overview": "", "genres": [], "keywords": []}
    parsed.setdefault("overview","")
    parsed.setdefault("genres", [])
    parsed.setdefault("keywords", [])
    return parsed

# ---------- 2) search indices ----------
def _search_index(index, text, k, weight):
    if weight <= 0 or not text.strip():
        return {}
    vec = _embed_text(text)
    if vec is None:
        return {}
    D, I = index.search(np.array([vec], dtype=np.float32), k)
    contrib = {}
    for dist, mid in zip(D[0], I[0]):
        if mid == -1: 
            continue
        sim = 1.0 / (1.0 + float(dist))  # convert L2 → similarity
        contrib[str(int(mid))] = contrib.get(str(int(mid)), 0.0) + sim * weight
    return contrib

def search_indices(parsed, weights, k=10):
    # load indices once
    idx_plot     = _load_index("plot")
    idx_overview = _load_index("overview")
    idx_genre    = _load_index("genre")
    idx_keyword  = _load_index("keyword")

    total = {}

    def accumulate(contrib):
        for mid, s in contrib.items():
            total[mid] = total.get(mid, 0.0) + s

    # plot (use overview text as proxy)
    accumulate(_search_index(idx_plot, parsed.get("overview",""), k, weights.get("plot",0)))
    # overview
    accumulate(_search_index(idx_overview, parsed.get("overview",""), k, weights.get("overview",0)))
    # genres
    accumulate(_search_index(idx_genre, _normalize_list(parsed.get("genres")), k, weights.get("genres",0)))
    # keywords
    accumulate(_search_index(idx_keyword, _normalize_list(parsed.get("keywords")), k, weights.get("keywords",0)))

    return sorted(total.items(), key=lambda x: x[1], reverse=True)[:k]

# ---------- 3) fetch metadata ----------
def fetch_movies_from_db(movie_ids):
    if not movie_ids:
        return {}
    conn = sqlite3.connect("horror_movies.db")
    cur = conn.cursor()
    qmarks = ",".join("?"*len(movie_ids))
    cur.execute(
        f"""SELECT id, title, overview, runtime, poster, release_date, rating
              FROM movies WHERE id IN ({qmarks})""",
        [int(i) for i in movie_ids]
    )
    rows = cur.fetchall()
    conn.close()
    return {str(row[0]): row for row in rows}

# ---------- 4) render ----------
# def display_results(ranked, meta_map):
#     cards = []
#     for mid, score in ranked:
#         row = meta_map.get(mid)
#         if not row: 
#             continue
#         _id, title, overview, runtime, poster, release_date, rating = row
#         poster_html = f"<img src='{poster}' style='width:100%;border-radius:6px'/>" if poster else ""
#         runtime_txt = f"{runtime} min" if runtime else "—"
#         rating_txt = f"{rating:.1f}" if rating else "—"
#         date_txt = release_date or "—"
#         cards.append(f"""
#         <div style="width:270px;margin:10px;padding:12px;border:1px solid #e5e7eb;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,.06);font-family:sans-serif">
#           {poster_html}
#           <h3 style="margin:8px 0 6px 0;font-size:16px">{title}</h3>
#           <div style="color:#555;font-size:12px;margin-bottom:6px">
#             <span><b>Runtime:</b> {runtime_txt}</span> •
#             <span><b>Date:</b> {date_txt}</span> •
#             <span><b>Rating:</b> {rating_txt}</span>
#           </div>
#           <p style="font-size:12px;color:#333;line-height:1.35">{(overview or '')[:220]}{'...' if overview and len(overview)>220 else ''}</p>
#           <div style="font-size:12px;color:#111"><b>Score:</b> {score:.3f}</div>
#         </div>
#         """)
#     display(HTML(f"<div style='display:flex;flex-wrap:wrap'>{''.join(cards)}</div>"))

# ---------- 5) full pipeline ----------
def search_movies(user_query, weights=None, k=10):
    if weights is None:
        weights = {"plot": 0.2, "overview": 0.5, "genres": 0.0, "keywords": 0.3}

    parsed = parse_query_with_llm(user_query)
    ranked = search_indices(parsed, weights, k=k)
    ids = [mid for mid, _ in ranked]
    meta_map = fetch_movies_from_db(ids)
    return ranked, meta_map