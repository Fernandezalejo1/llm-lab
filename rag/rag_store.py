"""Vector store mínimo para el lab: embeddings vía Ollama + coseno en numpy.

Por qué no ChromaDB todavía: baja ~200 MB de wheels y arriesga romper en
Python 3.14. Este store cubre la Fase 1 (retrieval + persistencia JSON/npy)
y es 100% transparente para aprender. Cuando haga falta filtros potentes
por metadata o colecciones, migramos a ChromaDB sin tocar el resto.
"""

import json
import math
import os
import re
from collections import Counter

import numpy as np
import requests

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "bge-m3")
TOKEN_RE = re.compile(r"[a-z0-9áéíóúüñ]+")

# Stopwords es/en para que el BM25 no premie ruido léxico
STOPWORDS = {
    "de", "la", "el", "en", "que", "qué", "y", "a", "los", "del", "se", "las",
    "por", "un", "una", "para", "con", "no", "su", "sus", "al", "lo", "como",
    "cómo", "más", "mas", "pero", "le", "ya", "o", "este", "esta", "estos",
    "estas", "si", "es", "son", "hay", "tiene", "tienen", "cuál", "cual",
    "cuáles", "cuales", "cuando", "cuándo", "donde", "dónde", "cuánto",
    "cuanto", "porque", "porqué", "mucho", "muy", "the", "and", "of", "to",
    "in", "a", "for", "on", "with", "is", "are", "it", "this", "that", "do",
    "does", "what", "why", "how", "which", "explicá", "deci", "según",
}


def embed_batch(texts, batch=16):
    """Embeddings vía Ollama /api/embed (corre en CPU). Vectores normalizados."""
    out = []
    for i in range(0, len(texts), batch):
        part = texts[i:i + batch]
        r = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": part},
            timeout=180,
        )
        r.raise_for_status()
        out.extend(r.json()["embeddings"])
    m = np.array(out, dtype=np.float32)
    m /= (np.linalg.norm(m, axis=1, keepdims=True) + 1e-12)
    return m


class VectorStore:
    def __init__(self):
        self.chunks = []
        self.vectors = None

    def build(self, chunks):
        self.chunks = chunks
        self.vectors = embed_batch([c["text"] for c in chunks])

    def save(self, directory):
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, "chunks.json"), "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False)
        np.save(os.path.join(directory, "vectors.npy"), self.vectors)

    @classmethod
    def load(cls, directory):
        vs = cls()
        with open(os.path.join(directory, "chunks.json"), encoding="utf-8") as f:
            vs.chunks = json.load(f)
        vs.vectors = np.load(os.path.join(directory, "vectors.npy"))
        vs._bm25_index()
        return vs

    def _tokens(self, text):
        return [t for t in TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]

    def _bm25_index(self):
        """Índice léxico BM25 (k1=1.5, b=0.75) construido sobre el mismo corpus."""
        self._doc_tokens = [Counter(self._tokens(c["text"])) for c in self.chunks]
        self._doc_len = np.array([sum(t.values()) for t in self._doc_tokens], dtype=float)
        self._avgdl = float(self._doc_len.mean() + 1e-9)
        n = len(self.chunks)
        df = Counter()
        for t in self._doc_tokens:
            df.update(t.keys())
        self._idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def _bm25_scores(self, q_tokens, k1=1.5, b=0.75):
        scores = np.zeros(len(self.chunks))
        for t in set(q_tokens):
            if t not in self._idf:
                continue
            idf = self._idf[t]
            for i, dt in enumerate(self._doc_tokens):
                f = dt.get(t, 0)
                if f:
                    scores[i] += (idf * f * (k1 + 1)
                                  / (f + k1 * (1 - b + b * self._doc_len[i] / self._avgdl)))
        return scores

    def query(self, text, k=5, mode="hybrid", alpha=0.5):
        q = embed_batch([text])[0]
        dense = self.vectors @ q
        if mode == "dense":
            scores = dense
        else:  # hybrid: mezcla denso + BM25, cada uno normalizado a [0,1]
            dmin, dmax = dense.min(), dense.max()
            dense_n = (dense - dmin) / (dmax - dmin + 1e-12)
            bm = self._bm25_scores(self._tokens(text))
            bmin, bmax = bm.min(), bm.max()
            bm_n = (bm - bmin) / (bmax - bmin + 1e-12)
            scores = alpha * dense_n + (1 - alpha) * bm_n
        idx = np.argsort(-scores)[:k]
        return [{"score": float(scores[i]), **self.chunks[int(i)]} for i in idx]