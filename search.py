import os
import re
import json
import time
import random
import sqlite3
import numpy as np
import faiss
from mistralai import Mistral
from dotenv import load_dotenv
import atexit
load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise RuntimeError("⚠️ Missing MISTRAL_API_KEY in .env")

client = Mistral(api_key=MISTRAL_API_KEY)

BASE_DIR = os.path.dirname(__file__)
DB_DIR   = os.path.join(BASE_DIR, "databases")

OVERVIEW_DB     = os.path.join(DB_DIR, "enriched_overview.db")
OVERVIEW_INDEX  = os.path.join(DB_DIR, "enriched_overview.index")
OVERVIEW_IDS    = os.path.join(DB_DIR, "enriched_overview_ids.npy")
RAW_DB          = os.path.join(DB_DIR, "horror_movies_clean.db")
INDEX = faiss.read_index(OVERVIEW_INDEX)
IDS   = np.load(OVERVIEW_IDS)
DB_CONN = sqlite3.connect(RAW_DB, check_same_thread=False)
USER_QUERY_PROMPT = "user_query_prompt.txt"
PROMPT_PATH = os.path.join(BASE_DIR, USER_QUERY_PROMPT)
EMBED_MODEL = "mistral-embed"
LLM = "mistral-small"



def safe_chat_call(messages, model=LLM, retries=5):
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

def _embed_text(text: str) -> np.ndarray | None:
    text = (text or "").strip()
    if not text:
        return None
    resp = client.embeddings.create(model=EMBED_MODEL, inputs=text)
    return np.array(resp.data[0].embedding, dtype=np.float32)

def _load_index(path):
    return faiss.read_index(path)


def parse_query_with_llm(user_query: str) -> dict:
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        FEW_SHOT_PROMPT = f.read()

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
        parsed = {"overview_focus": ""}
    parsed.setdefault("overview_focus", "")
    return parsed


def search_index_overview(overview_text, k=10):
    if not overview_text.strip():
        return []

    idx = INDEX
    ids = IDS

    vec = _embed_text(overview_text)
    if vec is None:
        return []

    vec = vec.reshape(1, -1).astype(np.float32)
    faiss.normalize_L2(vec)

    D, I = idx.search(vec, k)

    results = []
    for dist, idx_id in zip(D[0], I[0]):
        if idx_id == -1:
            continue
        mid = int(ids[idx_id])
        results.append((str(mid), float(dist)))
    return results

def fetch_movies_from_db(movie_ids):
    if not movie_ids:
        return {}
    cur = DB_CONN.cursor()
    qmarks = ",".join("?" * len(movie_ids))
    cur.execute(
        f"""SELECT id, title, overview, runtime, poster, release_date, rating
              FROM movies WHERE id IN ({qmarks})""",
        [int(i) for i in movie_ids]
    )
    rows = cur.fetchall()
    return {str(row[0]): row for row in rows}

def search_movies(user_query, k=10):
    parsed = parse_query_with_llm(user_query)
    overview_text = parsed.get("overview_focus", "")
    ranked = search_index_overview(overview_text, k=k)
    ids = [mid for mid, _ in ranked]
    meta_map = fetch_movies_from_db(ids)
    return ranked, meta_map

def close_db():
    DB_CONN.close()

atexit.register(close_db)