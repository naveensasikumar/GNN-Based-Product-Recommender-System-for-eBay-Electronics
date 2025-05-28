# GNN-Based-Product-Recommender-System-for-eBay-Electronics

This project implements a content-based recommendation system for electronics listings using Graph Neural Networks (GNNs). By encoding semantic similarities between products into a graph structure, the system learns meaningful item embeddings using GraphSAGE and serves product recommendations and item clusters via a FastAPI backend and an interactive React frontend.

---

## 📌 Project Overview

### Objective
To develop a scalable recommender system that suggests similar electronics listings on eBay based on item metadata, leveraging modern machine learning and graph-based techniques.

### Key Features
- **Graph Construction** based on semantic similarity of item titles (via Sentence-BERT)
- **GraphSAGE Embedding** to learn item-level representations
- **Product Recommendations** via cosine similarity on learned embeddings
- **Cluster Discovery** with KMeans for latent grouping
- **FastAPI REST Backend** to serve recommendations and cluster queries
- **React/Bootstrap Frontend** with filtering, item preview, and swipable layout

---

## 🛠️ Technologies Used

| Component        | Tools / Frameworks |
|------------------|--------------------|
| Programming Language | Python, JavaScript |
| Graph Modeling   | PyTorch Geometric, NetworkX |
| Embeddings       | SentenceTransformers (`all-MiniLM-L6-v2`) |
| GNN Architecture | GraphSAGE |
| Clustering       | KMeans (Scikit-learn) |
| API Server       | FastAPI |
| Frontend         | React.js, Bootstrap |
| Data Format      | eBay Electronics (JSONL, CSV) |

---

## 📊 System Architecture

1. **Data Preparation**  
   - Parse 10,000+ eBay electronics listings (title, price, image, etc.)
   - Encode product titles using Sentence-BERT
   - The full `combined.jsonl` file exceeds GitHub’s 100MB limit and is excluded.  
   - A sample (`sample_combined.jsonl`) with 500 listings is provided for demonstration.


2. **Graph Construction**  
   - Group by category → compute intra-group cosine similarities
   - Connect top-k most similar items to form edges
   - Output: `edge_index`, `x` (node features), item metadata

3. **GNN Training**  
   - Train a GraphSAGE model to learn item embeddings
   - Save learned representations for retrieval

4. **Recommendation Logic**  
   - For a given item (or list), retrieve top-N most similar items

5. **Clustering**  
   - Run KMeans on GNN embeddings to group products
   - Support "browse by cluster" feature in UI

6. **API + UI**  
   - FastAPI backend exposes `/recommend` and `/cluster-items` endpoints
   - React frontend allows users to input item IDs, browse clusters, and view recommendations

---

## 🧪 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/gnn-ebay-recommender.git
cd gnn-ebay-recommender
```

### 2. Backend Setup (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn fastapi_recommender:app --reload
```

### 3. Frontend Setup (React + Bootstrap)

```bash
cd frontend
npm install
npm start
```

---

## 🔍 Example Use Case

- A user views an item: `Apple AirPods Pro Replacement`
- The system finds its closest neighbors in the embedding space
- Returns top 10 similar listings with image, price, and short description
- User can also explore other items in the same cluster

---

## 📊 Clustering Insights

- KMeans clustering is applied on learned embeddings
- Enables:
  - Latent category discovery
  - Filtering UI
  - Visual browsing by cluster

---

## 📽️ Demo

![GNN Recommender Demo](demo/Demo.gif)




## Future Improvements

- Multi-modal GNN using text + image features
- Personalized recommendations using user session history
- Docker containerization for deployment
- Integration with live eBay APIs

---

## 📄 License

This project is licensed under the MIT License.  
© 2025 Naveen Sasikumar
