import streamlit as st
from dotenv import load_dotenv
from search import search_movies
import os
import base64

load_dotenv()
st.set_page_config(page_title="CineMantic 🎬", page_icon="🎬", layout="wide")
logo_path = os.path.join("assets", "tmdb_logo.svg")

st.markdown(
    """
    <h1 style="text-align:center; margin-bottom:0;">
        🎬 CineMantic
    </h1>
    <p style="text-align:center; color:gray; margin-top:4px;">
        Find your next horror experience with semantic search.
    </p>
    <p style="text-align:center; color:#d97706; margin-top:6px;">
        ⚠️ Alpha build — results may not be perfect
    </p>
    """,
    unsafe_allow_html=True,
)

MAX_TOKENS = 1024
query = st.text_area(
    "Summon your nightmare…",
    max_chars=MAX_TOKENS,
    placeholder="e.g., A haunted house story with ghosts tormenting a family...",
    height=120
)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    search_clicked = st.button("🔍 Find Movies", use_container_width=True)

if search_clicked:
    if not query.strip():
        st.warning("Please enter a description.")
    else:
        with st.spinner("🔮 Summoning...."):
            ranked, meta_map = search_movies(query, k=5)

        if not ranked:
            st.error("No matches found.")
        else:
            for mid, score in ranked:
                row = meta_map.get(mid)
                if not row:
                    continue
                _id, title, overview, runtime, poster, release_date, rating = row

                col1, col2 = st.columns([1, 3])
                with col1:
                    if poster:
                        st.image(poster, width=150)
                with col2:
                    st.subheader(title)
                    st.caption(f"⭐ {rating or '—'} | {runtime or '—'} min | {release_date or '—'}")
                    st.write(overview)

                    percent = int(max(0.0, min(score, 1.0)) * 100)
                    st.caption(f"Match: {percent}%")

                st.markdown("---")

with open(logo_path, "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
    <div style="text-align:center; margin-top:40px; margin-bottom:40px;">
        <p style="font-size:12px; color:gray; margin-bottom:12px;">
            This product uses the TMDB API but is not endorsed or certified by TMDB.
        </p>
        <img src="data:image/png;base64,{logo_base64}" width="140">
    </div>
    """,
    unsafe_allow_html=True,
)


with st.expander("ℹ️ About CineMantic"):
    st.markdown(
        """
        CineMantic is an experimental semantic search engine for horror movies.
        Instead of keyword matching, it understands **plots, themes, and vibes** — letting you search in natural language.

        **Current Version:** Alpha build.  
        Database currently includes the **Top 500 highest-rated horror titles on TMDB**.
        """
    )