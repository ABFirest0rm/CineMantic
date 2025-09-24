# 🎬👻 CineMantic – Semantic Horror Movie Finder  

CineMantic is a semantic search app for horror movies.  
Instead of typing exact titles, you can describe a scene, vibe, or fuzzy memory — *“creepy haunted house with ghosts tormenting a family”* — and CineMantic finds the closest matches.  

![CineMantic Screenshot](docs/screenshot.png) <!-- optional if you add a screenshot -->

---

## ✨ Features
- 🧠 **Mistral embeddings** for semantic understanding  
- ⚡ **FAISS vector search** for fast similarity lookups  
- 🎬 **SQLite movie database** 
- 🎨 **Streamlit frontend** with responsive UI  
- Weighted scoring from **plot, overview, keywords, genres**  
- Token-aware input (fits within model context)  
- Movie posters, ratings, runtime, and release dates shown  
- Proper **TMDB attribution**  

---

## 🛠 Tech Stack
- **Python 3.12**  
- **Mistral API** – embeddings + query parsing  
- **FAISS** – vector similarity  
- **SQLite** – lightweight movie DB  
- **Streamlit** – UI + deployment

