from sentence_transformers import SentenceTransformer
import numpy as np

# Global model instance (loaded once)
_model = None

def get_embedding_model():
    """Get or create the sentence transformer model (singleton pattern)."""
    global _model
    if _model is None:
        try:
            _model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Error loading main model: {e}")
            print("Using fallback model...")
            _model = SentenceTransformer('all-MiniLM-L3-v2')
    return _model

def get_embedding(text, model_name='all-MiniLM-L6-v2'):
    """Get embedding for text using cached sentence transformer model."""
    model = get_embedding_model()
    return model.encode(text, convert_to_numpy=True)

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
