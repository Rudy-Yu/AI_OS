"""
Vector Store — ChromaDB interface untuk AI_OS memory.
Handles penyimpanan dan retrieval memory jangka panjang.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    import chromadb
    _CHROMA_AVAILABLE = True
except Exception as e:  # pragma: no cover - import guard
    chromadb = None  # type: ignore[assignment]
    _CHROMA_AVAILABLE = False


from core.config import get_env
from core.logger import get_logger

logger = get_logger(__name__)

_CHROMA_PATH = get_env("CHROMA_PATH", "./chroma_db")

# Persistent client — data tersimpan di disk (jika Chroma tersedia)
if _CHROMA_AVAILABLE:
    client = chromadb.PersistentClient(path=_CHROMA_PATH)  # type: ignore[call-arg]
    collection = client.get_or_create_collection(
        name="ai_os_memory",
        metadata={"hnsw:space": "cosine"},
    )
else:
    client = None  # type: ignore[assignment]
    collection = None  # type: ignore[assignment]
    _MEM_FALLBACK: List[str] = []
    logger.error(
        "ChromaDB unavailable; falling back to in-process memory store. "
        "Install a Chroma-compatible numpy (<2.0) to enable vectors."
    )


def store(text: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """Simpan teks ke vector store."""
    try:
        if _CHROMA_AVAILABLE and collection is not None:
            doc_id = str(abs(hash(text)))
            collection.add(  # type: ignore[call-arg]
                documents=[text],
                ids=[doc_id],
                metadatas=[metadata or {}],
            )
            logger.info(f"Stored memory (chroma): {text[:50]}...")
        else:
            _MEM_FALLBACK.append(text)
            logger.info(f"Stored memory (fallback): {text[:50]}...")
        return True
    except Exception as e:
        logger.error(f"Failed to store memory: {e}")
        return False


def search(query: str, n_results: int = 3) -> List[str]:
    """Cari memory yang relevan dengan query."""
    try:
        if _CHROMA_AVAILABLE and collection is not None:
            total = collection.count() or 0  # type: ignore[call-arg]
            if total <= 0:
                logger.info("Memory search requested but collection is empty")
                return []
            result = collection.query(  # type: ignore[call-arg]
                query_texts=[query],
                n_results=min(n_results, total),
            )
            docs = result["documents"][0] if result.get("documents") else []
            logger.info(f"Found {len(docs)} memories for query: {query[:50]}")
            return docs

        # Fallback: naive substring search.
        hits = [t for t in _MEM_FALLBACK if query.lower() in t.lower()]
        logger.info(
            f"Found {len(hits)} fallback memories for query: {query[:50]}"
        )
        return hits[:n_results]
    except Exception as e:
        logger.error(f"Memory search failed: {e}")
        return []


def clear() -> bool:
    """Hapus semua memory."""
    try:
        global collection
        if _CHROMA_AVAILABLE and client is not None:
            client.delete_collection("ai_os_memory")  # type: ignore[call-arg]
            collection = client.get_or_create_collection(  # type: ignore[call-arg]
                "ai_os_memory"
            )
            logger.info("Memory cleared successfully (chroma)")
        else:
            _MEM_FALLBACK.clear()
            logger.info("Memory cleared successfully (fallback)")
        return True
    except Exception as e:
        logger.error(f"Failed to clear memory: {e}")
        return False


def count() -> int:
    """Return jumlah item di memory."""
    try:
        if _CHROMA_AVAILABLE and collection is not None:
            return int(collection.count() or 0)  # type: ignore[call-arg]
        return len(_MEM_FALLBACK)
    except Exception as e:
        logger.error(f"Failed to count memory: {e}")
        return 0

