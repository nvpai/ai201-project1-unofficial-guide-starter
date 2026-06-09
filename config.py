import os
from dotenv import load_dotenv

load_dotenv()

# --- LLM ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LLM_MODEL = "llama-3.3-70b-versatile"

# --- Embeddings ---
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# --- Vector store ---
CHROMA_COLLECTION = "reviewBot"
CHROMA_PATH = "./chroma_db"

# --- Retrieval ---
N_RESULTS = 3

# --- Documents ---
DOCS_PATH = "./documents"

# --- Chunking ---
# Target ~256 tokens because all-MiniLM-L6-v2 truncates anything longer at
# embedding time, so a 500-token chunk would only be half-"seen" during
# retrieval. Overlap of 50 tokens (~20%) preserves context across the
# boundaries the structure-aware splitter has to cut.
CHUNK_MAX_TOKENS = 256
CHUNK_OVERLAP_TOKENS = 50
CHUNK_MIN_TOKENS = 20
