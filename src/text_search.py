"""
SkyJames - Text-to-Video Search (Simplified)
Uses TF-IDF instead of transformers for compatibility
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import cv2
import os
import json

class VideoSearch:
    def __init__(self):
        self.video_metadata = []
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.tfidf_matrix = None
        self.descriptions = []
    
    def index_video(self, video_path, description, metadata=None):
        """Index a video with description"""
        self.descriptions.append(description)
        self.video_metadata.append({
            'path': video_path,
            'description': description,
            'metadata': metadata or {},
            'index': len(self.video_metadata)
        })
        
        # Update TF-IDF matrix
        if len(self.descriptions) > 1:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.descriptions)
        else:
            self.tfidf_matrix = None
        
        return len(self.video_metadata) - 1
    
    def search(self, query, top_k=5):
        """Search videos by text query"""
        if not self.video_metadata:
            return []
        
        # Fit vectorizer if not done
        if self.tfidf_matrix is None and len(self.descriptions) > 0:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.descriptions)
        
        if self.tfidf_matrix is None:
            return []
        
        # Transform query
        query_vector = self.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        
        # Get top results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:
                results.append({
                    'video': self.video_metadata[idx],
                    'score': float(similarities[idx])
                })
        
        return results
    
    def save_index(self, path="data/search_index.json"):
        """Save search index to file"""
        data = {
            'descriptions': self.descriptions,
            'metadata': self.video_metadata
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        return path
    
    def load_index(self, path="data/search_index.json"):
        """Load search index from file"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            self.descriptions = data['descriptions']
            self.video_metadata = data['metadata']
            if self.descriptions:
                self.tfidf_matrix = self.vectorizer.fit_transform(self.descriptions)
            return True
        except:
            return False

# Test function
def test_search():
    print("🚀 Testing Video Search...")
    
    search = VideoSearch()
    
    # Index sample videos
    search.index_video("video1.mp4", "Highway driving with lane detection")
    search.index_video("video2.mp4", "City street with pedestrians and cars")
    search.index_video("video3.mp4", "Night driving with headlights")
    search.index_video("video4.mp4", "Parking lot with obstacles")
    
    # Search
    results = search.search("driving on highway")
    print("\n📊 Search Results for 'driving on highway':")
    for r in results:
        print(f"  - {r['video']['description']} (Score: {r['score']:.2f})")
    
    results = search.search("pedestrians in city")
    print("\n📊 Search Results for 'pedestrians in city':")
    for r in results:
        print(f"  - {r['video']['description']} (Score: {r['score']:.2f})")
    
    # Save index
    search.save_index()
    print("\n✅ Search index saved to data/search_index.json")
    
    return search

if __name__ == "__main__":
    test_search()
