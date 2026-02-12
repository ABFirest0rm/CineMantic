# 🎬👻 CineMantic – Search by Vibe or Memory, Not Title

Ever wanted to find a movie with a certain vibe?

A setting. A feeling. Like:
- *Surreal horror set in remote Scottish mountains*

Or maybe you remember fragments of something you watched years ago, like:
- *Antarctic alien that imitates humans*
- *Girl crawling out of a TV*

…but not the name.

CineMantic lets you search for movies the way humans actually remember them —  
by **vibes, scenes, and fragments of plot**, not exact titles.

> *It’s not just search. It’s a vibe check for your watchlist.*

---

## 🌐 **Live Demo:**  
https://cinemantic.onrender.com/

> ⚠️ Initial load may take a moment due to cold starts on free-tier hosting and the demo may occasionally be unavailable due to API rate limits or service tier restrictions.

---

<img width="1280" height="768" alt="main" src="https://github.com/user-attachments/assets/0e4bfa3d-2d12-4ac3-a6a0-512e62dc2a2e" />

- Search example

<img width="1280" height="773" alt="thing" src="https://github.com/user-attachments/assets/7ce6862d-468a-455e-8eef-253d218977f5" />

- Search example

<img width="2520" height="1581" alt="feel2" src="https://github.com/user-attachments/assets/f7d546e3-1b7a-4d55-a270-defb459f29a7" />

---



## 💡 Why I Built This?

I love horror movies.

But I kept running into the same problem:

- Sometimes I’d be in the mood for something specific — atmospheric, isolating, psychological.
- Other times, I’d remember bits of a movie from years ago… but not the title.

Forums and Google searches were hit-or-miss and time-consuming.

Traditional search expects keywords.  
Human memory doesn’t work like that.

So I built 🎬👻 **CineMantic** — a small experiment in semantic movie discovery.

---

## ✨ What It Does?

- 🧠 Understands plot fragments and conceptual descriptions from user input  
- ⚡ Uses vector similarity search to retrieve the closest matches  
- 🎬 Displays posters, TMDB ratings, runtime, and release dates  
- 🌙 Clean, dark-themed interface built with **Streamlit**

Instead of typing exact names, you describe what you feel or remember.

---

## 🧩 How It Works (Under the Hood)?

> The system follows a retrieval-first architecture inspired by modern RAG pipelines, separating query understanding, vector search, and metadata enrichment.


### 1️⃣ Query Normalization (LLM-Assisted)

User input is normalized using an LLM to bridge the gap between fuzzy human descriptions and structured TMDB-style movie overviews.

This improves alignment before embedding and helps semantic retrieval perform more accurately.

---

### 2️⃣ Semantic Embeddings  

Both user queries and movie overviews are transformed into dense vector representations using a transformer-based embedding model.

These vectors capture conceptual similarity beyond simple keyword overlap.

---

### 3️⃣ High-Dimensional Vector Search (FAISS)

All movie overview embeddings are indexed using **FAISS** for efficient nearest-neighbor search.

When you search:
- Your query is embedded into the same vector space  
- FAISS retrieves the top-k nearest neighbors  
- Results are ranked by similarity score  

---

### 4️⃣ Metadata Enrichment Layer  

Matched vector IDs are joined with a lightweight SQLite database to retrieve posters, ratings, runtime, and release data.


---

## 🔍 Example Query Flow

**Input:**  
`psychological thriller with shocking plot twists`

**Process:**
- Query → normalized via LLM  
- Query → embedding vector  
- FAISS → top k nearest overviews  
- SQLite → retrieve metadata

**Output:**  
Ranked movies with similarity scores and full context.

---

## 🎃 Dataset & Scope

This prototype currently indexes:

**Top 500 highest-rated horror films on TMDB**

While the demo focuses on horror, the retrieval architecture is genre-agnostic and can scale to larger datasets.

---

## 🤖 Models Used

CineMantic uses Mistral models for both:

- LLM-assisted query normalization

- Text embeddings generation

---

## 📌 Disclaimer

This product uses the TMDB API but is not endorsed or certified by TMDB.

## 🚀 Running Locally

```bash
git clone https://github.com/ABFirest0rm/cinemantic.git
cd cinemantic
pip install -r requirements.txt
streamlit run app.py
```

> ⚠️ Before running locally, create a `.env` file:
>
> ```
> MISTRAL_API_KEY=your_key_here
> ```
>
> Use your own API key. Model names or API calls may need small adjustments depending on what’s available to you.
