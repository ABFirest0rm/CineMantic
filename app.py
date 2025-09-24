import streamlit as st
from dotenv import load_dotenv
import os
from search import search_movies  # your pipeline

# Load env (for API keys etc.)
load_dotenv()

# Page config
st.set_page_config(page_title="Cinemantic 🎬", page_icon="🎬", layout="wide")

# Title & tagline
st.markdown(
    """
    <h1 style="text-align:center; margin-bottom:0;">
        🎬 Cinemantic
    </h1>
    <p style="text-align:center; color:gray; margin-top:4px;">
        Find your next horror experience with semantic search.
    </p>
    """,
    unsafe_allow_html=True,
)

# Token-aware input
MAX_TOKENS = 1024
query = st.text_area(
    "Describe the movie you want to watch:",
    max_chars=MAX_TOKENS,
    placeholder="e.g., A haunted house story with ghosts tormenting a family...",
    height=120
)

# Centered search button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    search_clicked = st.button("🔍 Find Movies", use_container_width=True)

# Handle search
if search_clicked:
    if not query.strip():
        st.warning("Please enter a description.")
    else:
        with st.spinner("🔮 Summoning movies..."):
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
                    st.write(f"**Score:** {score:.3f}")
                st.markdown("---")

# TMDB Attribution
st.markdown(
    """
    <p style="text-align:center; font-size:12px; color:gray; margin-top:40px;">
        This product uses the TMDB API but is not endorsed or certified by TMDB.<br>
        <img src="https://www.themoviedb.org/assets/2/v4/logos/v2/blue_square_2-d537fb228cf3ded904ef09b136fe3fec72548ebc1fea3fbbd1ad9e36364db38b.svg"
             width="80">
    </p>
    """,
    unsafe_allow_html=True,
)
