# ⚽ TactiVision AI

### AI-Powered Soccer Intelligence & Tactical Decision Support Platform

TactiVision AI is an end-to-end soccer analytics platform designed to transform event-level football data into actionable intelligence for coaches, analysts, scouts, and recruitment teams.

The platform combines **football analytics, machine learning, player similarity modeling, tactical visualization, and a citation-grounded AI assistant** into a single product experience.

Instead of simply presenting raw statistics, TactiVision AI is designed around a more practical question:

> **"What should a coach, analyst, or scout do with this information?"**

---

## 🚀 Live Product

### 🌐 Frontend

**Live Application:**  
https://tacti-vision-ai211.vercel.app/

### ⚙️ Backend API

**Backend:**  
https://tactivision-backend-production.up.railway.app

### 📦 Source Code

**GitHub Repository:**  
https://github.com/swyam1104/TactiVision-AI

---

# 📌 Product Overview

Modern football departments work with enormous amounts of event-level match data.

However, raw data alone does not automatically produce useful football intelligence.

TactiVision AI attempts to bridge that gap by transforming event data into:

- Expected Goals (xG) analysis
- Player performance profiles
- Player similarity recommendations
- Passing network visualization
- Tactical insights
- Match-level statistical intelligence
- AI-powered football Q&A
- Explainable machine-learning outputs

The platform uses **StatsBomb Open Data** as its primary event-data source and processes match events into structured analytical features.

---

# 🎯 Why TactiVision AI?

Football analytics tools often suffer from one of two problems:

1. They provide large amounts of data without enough interpretation.
2. They provide AI-generated insights without sufficient grounding in actual match data.

TactiVision AI was designed to explore a middle ground:

> **Data → Analytics → Intelligence → Decision Support**

The goal is not to replace coaches or analysts.

The goal is to help them **find relevant information faster and make better-informed decisions.**

---

# 🧠 Core Features

## 1. 📈 Expected Goals (xG) Model

TactiVision AI includes an explainable Expected Goals model designed to estimate the probability that a shot results in a goal.

The model uses contextual shot features including:

- Shot location
- Distance from goal
- Shooting angle
- Body part
- Shot type
- Header vs foot
- Volley
- Direct free-kick
- Defensive pressure
- Other event-level shot characteristics

The system supports machine-learning experimentation using:

- XGBoost
- Logistic Regression
- Scikit-learn
- SHAP

### Why it matters

Rather than simply showing:

> "Player X took 5 shots."

the system can help answer:

> "How valuable were those chances?"

and:

> "Which factors contributed most to the model's prediction?"

---

# 2. 👤 Player Similarity Engine

The Player Similarity Engine compares players based on their underlying performance profiles rather than simply comparing goals or assists.

Player statistics are normalized on a **per-90-minute basis** to make comparisons more meaningful.

The system considers metrics such as:

- Goals
- Key passes
- Carries
- Tackles
- Recoveries
- Pressures
- Shots
- Shot accuracy
- Other event-derived performance indicators

A nearest-neighbor approach using **cosine similarity** is then used to identify players with comparable profiles.

### Example Use Case

A recruitment analyst could ask:

> "Find players who have a similar statistical profile to this midfielder."

The system can return comparable player profiles and visualize their relative characteristics.

---

# 3. 🗺️ Player Similarity Visualization

The similarity engine can project player vectors into a two-dimensional representation using **UMAP**.

This provides an intuitive visual representation of player clusters.

Players with similar statistical profiles appear closer together, allowing analysts to identify:

- Similar player archetypes
- Potential recruitment targets
- Statistical outliers
- Position-specific clusters
- Players with unusual profiles

---

# 4. 🔗 Passing Network Analysis

TactiVision AI processes event-level passing data to construct passing networks.

These visualizations can help analyze:

- Passing relationships
- Central players
- Possession structure
- Ball progression patterns
- Team connectivity
- Potential tactical bottlenecks

Instead of viewing passing events individually, analysts can examine the broader structure of a team's possession.

---

# 5. 🤖 AI Coach Assistant

TactiVision AI includes an AI-powered tactical assistant designed around **Retrieval-Augmented Generation (RAG)**.

The assistant can answer questions about football data and match statistics while grounding responses in available match information.

The system combines:

- Semantic retrieval
- Match statistics
- Structured football data
- Event information
- Vector search
- Large Language Models

The objective is to reduce unsupported AI answers by grounding responses in the platform's underlying football data.

### Example Questions

```text
Which players created the most chances?

Which players had the strongest attacking output?

Who are the most similar players to this midfielder?

Which team generated better shot quality?

What explains the difference in attacking performance?

Which players appear most involved in progression?
