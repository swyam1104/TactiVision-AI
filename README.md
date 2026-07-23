# TactiVision AI — Soccer Intelligence & Tactical Analysis Platform

TactiVision AI is an end-to-end soccer analytics and tactical decision support system designed for modern coaching and recruitment departments. The platform ingests event-level match data, engineers specialized spatial features, trains an explainable Expected Goals (xG) model, runs player similarity nearest-neighbors comparisons, maps passing networks, and serves a citation-grounded RAG (Retrieval-Augmented Generation) assistant.

## Why I Built This

I built TactiVision AI because I wanted to explore how event-level spatial data can be translated into actionable intelligence for coaches. As a fan of tactical football, I wanted to see if I could build a lightweight, explainable model using StatsBomb's open data that mimics what modern recruitment and analysis departments use.

---

## 1. System Architecture

```
                                  [ Next.js Attacking Dashboard (Port 3000) ]
                                                      │
                                                      ▼ (REST JSON API)
                                    [ FastAPI Backend Service (Port 8000) ]
                                     /             │                │            \
                                    /              │                │             \
                                   ▼               ▼                ▼              ▼
                              [ Postgres ]   [ Redis + Celery ]  [ ML Models ]  [ Vector DB (FAISS) ]
                              - Competitions  - Message Broker   - xG (XGBoost) - Match facts
                              - Matches       - Async Tasks      - Cosine Sim   - Event snippets
                              - Events                           - UMAP Coords
                              - Lineups
```

- **Data Pipeline**: Idempotent download and ingestion of StatsBomb Open Data. Restructures raw nested event sheets into a normalized PostgreSQL schema (`competitions`, `matches`, `teams`, `players`, `lineups`, `events`).
- **Explainable ML (xG)**: Fits XGBoost and Logistic Regression on shot features (goalmouth distance, shooting angle, body part, shot category, under pressure). Yields full ROC-AUC evaluation and SHAP feature importance.
- **Player Similarity**: Aggregated event statistics per player per-90 minutes are scaled using standard normalization. A Nearest Neighbors model with cosine distance calculates top matches, visualized in a UMAP 2D coordinates map.
- **Coach Assistant (RAG)**: Uses semantic similarity matching over match statistics and fact sheets. Uses an LLM to answer complex tactical questions with inline citations.

### Key Challenges & Learnings
- **Handling Class Imbalance**: Goals are rare events (~10% of shots). Addressed this in XGBoost by tuning `scale_pos_weight` and evaluating with PR-AUC alongside standard ROC-AUC.
- **Normalization & Noise Reduction**: Stats were normalized per-90 minutes while filtering out low-sample substitute players to keep player similarity search accurate and prevent skewed vectors.

---

## 2. Quickstart (Docker Compose)

To start the entire stack (PostgreSQL + Redis + FastAPI Backend + Celery Worker + Next.js UI) in a containerized environment, simply execute:

```bash
docker compose up --build
```

- **Next.js Attacking UI**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Backend Swagger**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Database URL**: `postgresql://postgres:postgres@localhost:5432/tactivision`

*Note: On boot, the FastAPI application automatically initializes database tables, runs the ingestion pipeline for a sample of StatsBomb open data (2018 World Cup & 2015/16 Premier League), trains the initial models, and populates the similarity vector cache.*

---

## 3. Local Development (Manual Setup)

### Backend Setup
1. Create a virtual environment and install packages:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Set configuration parameters in a local `.env` file (optional, defaults are set in `app/core/config.py`):
   ```env
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tactivision
   REDIS_URL=redis://localhost:6379/0
   OPENAI_API_KEY=your_key_here
   ```
3. Run the startup script to load data and train initial models:
   ```bash
   python ml/etl/ingest.py
   python ml/xg_model/train.py
   python ml/similarity/train_similarity.py
   ```
4. Run tests:
   ```bash
   pytest tests/ -v
   ```
5. Run the web server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup
1. Install Node packages and run the development server:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. Access the dashboard at `http://localhost:3000`.

---

## 4. Analytical Features & ML Details

### Expected Goals (xG) Features
- **Distance**: Calculated as Euclidean distance to center of goal mouth `(120, 40)`.
- **Visible Goal Angle**: The angle in radians spanning between the goalposts `(120, 36)` and `(120, 44)`.
- **Shot Modifiers**: Categorical binary mappings for headers vs feet, volley shots, direct free-kicks, and defensive pressures.

### Player Similarity Index
- Compiles 12 normalized per-90 metrics (goals, key passes, carries, tackles, recoveries, pressures, shot accuracy, etc.).
- Measures similarity using **Cosine Distance**:
  $$\text{Cosine Similarity} = 1 - d_{\text{cosine}} = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$
- Compares Query and Match candidates side-by-side using percentile metrics mapped on a radar chart.
