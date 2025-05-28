from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import torch
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def clean_value(v):
    if isinstance(v, float) and (pd.isna(v) or not np.isfinite(v)):
        return ""
    return v

# Load data
with open("combined.jsonl") as f:
    items = [json.loads(line) for line in f]

embs = torch.load("ebay_item_embeddings_sage.pt").cpu().numpy()
id2idx = {item["itemId"]: i for i, item in enumerate(items)}
idx2item = {i: item for i, item in enumerate(items)}

class RecommendRequest(BaseModel):
    user_item_id: str
    top_k: int = 10
    category_name: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    condition: Optional[str] = None

@app.post("/recommend")
def recommend(req: RecommendRequest):
    if req.user_item_id not in id2idx:
        return {"error": "Item ID not found"}

    item_index = id2idx[req.user_item_id]
    user_vector = embs[item_index].reshape(1, -1)
    sims = cosine_similarity(user_vector, embs)[0]
    ranked = sims.argsort()[::-1]

    recommendations = []
    for idx in ranked:
        if idx == item_index:
            continue
        item = idx2item[idx]

        # Filters
        if req.category_name and item.get("categoryName", "").lower() != req.category_name.lower():
            continue
        cond = item.get("condition", "")
        cond_display = cond.get("conditionDisplayName", "") if isinstance(cond, dict) else cond
        if req.condition and cond_display.lower() != req.condition.lower():
            continue
        price_str = item.get("price", {}).get("value", "0")
        try:
            price_val = float(price_str)
        except:
            price_val = 0.0
        if req.min_price and price_val < req.min_price:
            continue
        if req.max_price and price_val > req.max_price:
            continue

        # Aspects
        aspects = item.get("localizedAspects", {})
        aspect_summary = {}
        if isinstance(aspects, dict):
            aspect_summary = {k: v[0] if isinstance(v, list) else v for k, v in aspects.items()}
        elif isinstance(aspects, list):
            for aspect in aspects:
                if isinstance(aspect, dict):
                    for k, v in aspect.items():
                        aspect_summary[k] = v[0] if isinstance(v, list) else v

        recommendations.append({
            "itemId": item.get("itemId"),
            "title": item.get("title", ""),
            "price": item.get("price", {}),
            "image": item.get("image", {}).get("imageUrl", "https://via.placeholder.com/200"),
            "shortDescription": item.get("shortDescription") or item.get("subtitle") or "",
            "category_name": item.get("categoryName", ""),
            "condition": cond_display,
            "seller_username": item.get("seller", {}).get("username", ""),
            "shipping": item.get("shippingOptions", [{}])[0].get("shippingCost", {}).get("value", ""),
            "location": item.get("itemLocation", {}).get("postalCode", ""),
            "aspects": aspect_summary
        })

        if len(recommendations) == req.top_k:
            break

    # Viewed item
    viewed = idx2item[item_index]
    cond = viewed.get("condition", "")
    cond_display = cond.get("conditionDisplayName", "") if isinstance(cond, dict) else cond
    aspects = viewed.get("localizedAspects", {})
    aspect_summary = {}
    if isinstance(aspects, dict):
        aspect_summary = {k: v[0] if isinstance(v, list) else v for k, v in aspects.items()}
    elif isinstance(aspects, list):
        for aspect in aspects:
            if isinstance(aspect, dict):
                for k, v in aspect.items():
                    aspect_summary[k] = v[0] if isinstance(v, list) else v

    viewed_metadata = {
        "itemId": viewed.get("itemId"),
        "title": viewed.get("title", ""),
        "price": viewed.get("price", {}),
        "image": viewed.get("image", {}).get("imageUrl", "https://via.placeholder.com/200"),
        "shortDescription": viewed.get("shortDescription") or viewed.get("subtitle") or "",
        "category_name": viewed.get("categoryName", ""),
        "condition": cond_display,
        "seller_username": viewed.get("seller", {}).get("username", ""),
        "shipping": viewed.get("shippingOptions", [{}])[0].get("shippingCost", {}).get("value", ""),
        "location": viewed.get("itemLocation", {}).get("postalCode", ""),
        "aspects": aspect_summary
    }

    return {
        "viewed_item": viewed_metadata,
        "recommendations": recommendations
    }


clustered_df = pd.read_csv("ebay_clustered_items.csv")

@app.get("/browse-cluster/{cluster_id}")
def browse_by_cluster(cluster_id: int, limit: int = 10):
    cluster_items = clustered_df[clustered_df["cluster_id"] == cluster_id].head(limit)
    results = []

    for _, item in cluster_items.iterrows():
        results.append({
            "itemId": item.get("itemId"),
            "title": item.get("title"),
            "category_name": item.get("category_name", ""),
            "image": item.get("image_url", "https://via.placeholder.com/200"),
            "cluster_id": int(item["cluster_id"]),
            "price": item.get("price.value", ""),
            "condition": item.get("condition", ""),
            "seller_username": item.get("seller_username", "")
        })

    return {"cluster_id": cluster_id, "items": results}

@app.get("/cluster-items/{item_id}")
def get_items_from_same_cluster(item_id: str, limit: int = 10):
    if item_id not in clustered_df["itemId"].values:
        return {"error": "Item ID not found"}

    item_cluster = clustered_df[clustered_df["itemId"] == item_id]["cluster_id"].iloc[0]
    cluster_items = clustered_df[clustered_df["cluster_id"] == item_cluster].head(limit)

    results = []
    for _, item in cluster_items.iterrows():
        results.append({
    "itemId": clean_value(item.get("itemId")),
    "title": clean_value(item.get("title")),
    "category_name": clean_value(item.get("category_name")),
    "image": clean_value(item.get("image_url", "https://via.placeholder.com/200")),
    "cluster_id": int(item["cluster_id"]),
    "price": clean_value(item.get("price_value", "")),
    "condition": clean_value(item.get("condition")),
    "seller_username": clean_value(item.get("seller_username")),
})


    return {
        "cluster_id": int(item_cluster),
        "items": results
    }
