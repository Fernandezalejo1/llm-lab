#!/usr/bin/env python3
"""Indexa el corpus en rag/corpus/contabilia -> chunks + embeddings.

v2 — chunking fence-aware:
    Los bloques de código (```) quedan ATOMICOS: no se parten a mitad de
    función. (v1 partía por \n\n dentro del código y generaba micro-chunks
    de 3 líneas, ej. chunk 535 con solo `similarDesc` + trigramSimilarity,
    que el retrieval no recuperaba.)

Uso: python index_rag.py
Salida: rag/data/chunks.json + rag/data/vectors.npy
"""

import re
from pathlib import Path

from rag_store import EMBED_MODEL, VectorStore

CORPUS = Path("corpus/contabilia")
DATA = Path("data")

MAX_CHARS = 1200   # tope por segmento de prosa
CODE_CAP = 8000    # tope duro para un bloque de código aislado

SKIP_EXT = {".csv", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
            ".woff", ".woff2", ".apk", ".zip", ".lock", ".map"}
SKIP_DIRS = {"node_modules", ".git", "dist", "build", "venv", ".next",
             "coverage", "screenshots"}


def split_sections(text):
    """Secciones por #/##/###, sin romper dentro de un fence."""
    sections, cur, in_fence = [], [], False
    for line in text.splitlines():
        st = line.strip()
        if st.startswith("```"):
            in_fence = not in_fence
            cur.append(line)
        elif not in_fence and re.match(r"^#{1,3} ", line) and cur:
            sections.append("\n".join(cur).strip())
            cur = [line]
        else:
            cur.append(line)
    if cur:
        sections.append("\n".join(cur).strip())
    return [s for s in sections if s]


def tokenize_section(section):
    """('prose', texto) | ('code', texto) — los fences quedan íntegros."""
    tokens, buf, lines = [], [], section.splitlines()
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if line.strip().startswith("```"):
            if buf:
                tokens.append(("prose", "\n".join(buf)))
                buf = []
            code = []
            while i < n:
                code.append(lines[i])
                i += 1
                if lines[i - 1].strip().startswith("```"):
                    break
            tokens.append(("code", "\n".join(code)))
        else:
            buf.append(line)
            i += 1
    if buf:
        tokens.append(("prose", "\n".join(buf)))
    return tokens


def pack_tokens(tokens, max_chars=MAX_CHARS, code_cap=CODE_CAP):
    """Chunks <= max_chars; bloques de código enteros hasta code_cap."""
    out, cur, cur_len = [], [], 0

    def flush():
        nonlocal cur, cur_len
        if cur:
            text = "\n".join(cur).strip()
            if text:
                out.append(text)
        cur, cur_len = [], 0

    for kind, text in tokens:
        add = len(text) + 1
        if kind == "code":
            if len(text) > code_cap:
                flush()
                for p in text.split("\n\n"):
                    p = p.strip()
                    if p:
                        out.append(p[:code_cap])
                continue
            if cur and cur_len + add > max_chars:
                flush()
            cur.append(text)
            cur_len += add
        else:
            for para in re.split(r"\n(?=\S)", text):
                if cur and cur_len + len(para) + 1 > max_chars:
                    flush()
                while len(para) > max_chars:
                    flush()
                    out.append(para[:max_chars])
                    para = para[max_chars:]
                if para:
                    cur.append(para)
                    cur_len += len(para) + 1
    flush()
    return out


def chunk_markdown(text):
    out = []
    for s in split_sections(text):
        out.extend(pack_tokens(tokenize_section(s)))
    return out


def chunk_code(text, rel):
    """Párrafos contiguos agrupados, con referencia al archivo al inicio."""
    heads = re.split(r"\n\s*\n", text)
    out, cur = [], f"# archivo: {rel}\n"
    for p in heads:
        p = p.strip()
        if not p:
            continue
        if len(cur) + len(p) + 1 > MAX_CHARS:
            out.append(cur.strip())
            cur = f"# archivo: {rel}\n"
        cur += p + "\n"
    if cur.strip():
        out.append(cur.strip())
    return out


def main():
    chunks, files = [], 0
    for p in sorted(CORPUS.rglob("*")):
        if not p.is_file() or p.suffix.lower() in SKIP_EXT:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = p.relative_to(CORPUS).as_posix()
        try:
            text = p.read_text(encoding="utf-8", errors="replace").strip()
        except Exception:
            continue
        if not text:
            continue
        files += 1
        pieces = chunk_markdown(text) if p.suffix.lower() == ".md" else chunk_code(text, rel)
        for i, c in enumerate(pieces):
            if c.strip():
                chunks.append({"id": f"{rel}#{i}", "file": rel,
                               "ext": p.suffix.lower(), "text": c[:CODE_CAP]})

    print(f"archivos: {files} | chunks: {len(chunks)}")
    vs = VectorStore()
    vs.build(chunks)
    vs.save(str(DATA))
    print(f"embeddings ({EMBED_MODEL}): {vs.vectors.shape} | guardado en {DATA}/")


if __name__ == "__main__":
    main()