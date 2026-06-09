"""
Milestone 3 — Document ingestion and chunking.

Pipeline stage [1] + [2] from planning.md:

    DOCUMENT INGESTION  ->  CHUNKING (structure-aware, ~256 tokens, 50 overlap)

The corpus is student-written commentary on UT Austin's online MSCSO / MSDSO
programs, collected as plain .txt files in ./documents. Two document shapes:

  * Reddit threads  — a metadata header, an "Original Post:", then "Comment N:"
                      / "User X:" replies. Split into the post and each comment
                      so every chunk is one self-contained opinion.
  * Blog posts      — a metadata header, then long-form prose. Split on
                      paragraph boundaries and packed up to the token budget.

Anything longer than CHUNK_MAX_TOKENS is further split with a token-level
sliding window (with overlap) using the *actual* all-MiniLM-L6-v2 tokenizer,
so chunk sizes line up with what the embedding model will really see.

Run this file directly to load, chunk, and inspect the output:

    python ingest.py
"""

import os
import re
import html

from config import (
    DOCS_PATH,
    EMBEDDING_MODEL,
    CHUNK_MAX_TOKENS,
    CHUNK_OVERLAP_TOKENS,
    CHUNK_MIN_TOKENS,
)


# ---------------------------------------------------------------------------
# Tokenizer — load the real embedding-model tokenizer so token counts match
# what all-MiniLM-L6-v2 will actually process at embedding time.
# Loaded lazily and cached: importing this module stays cheap, and only the
# small tokenizer files (vocab, not the model weights) are downloaded.
# ---------------------------------------------------------------------------

_tokenizer = None


def _get_tokenizer():
    global _tokenizer
    if _tokenizer is None:
        from transformers import AutoTokenizer
        _tokenizer = AutoTokenizer.from_pretrained(
            f"sentence-transformers/{EMBEDDING_MODEL}"
        )
    return _tokenizer


def count_tokens(text):
    """Number of wordpiece tokens, as the embedding model counts them."""
    return len(_get_tokenizer().encode(text, add_special_tokens=False))


# ---------------------------------------------------------------------------
# Loading + cleaning
# ---------------------------------------------------------------------------

# Leading "key: value" lines we treat as document metadata, e.g.
#   title: ... / source: ... / url: ... / program: MSCSO
_META_LINE = re.compile(r"^([A-Za-z][A-Za-z_ ]{1,18}):\s*(.*)$")


def _parse_header(text):
    """
    Pull the contiguous "key: value" metadata block off the top of a document.

    Returns (metadata_dict, body_text). Header parsing stops at the first blank
    line or the first line that isn't a key: value pair, so body content like
    "Pros:" or "Step 1 : Why MS Online?" is never mistaken for metadata.
    """
    meta = {}
    lines = text.splitlines()
    body_start = 0

    for i, line in enumerate(lines):
        if not line.strip():
            body_start = i + 1
            if meta:
                break          # blank line after the header => header is done
            continue           # skip leading blank lines before any metadata
        m = _META_LINE.match(line.strip())
        if m:
            meta[m.group(1).strip().lower()] = m.group(2).strip()
            body_start = i + 1
        else:
            body_start = i      # first real body line
            break

    body = "\n".join(lines[body_start:]).strip()
    return meta, body


def clean_text(text):
    """
    Light cleaning for already-plaintext sources.

    Removes any stray HTML tags/entities and collapses runs of blank lines.
    These files were copied by hand rather than scraped, so there's little
    boilerplate to strip — but we still guard against HTML artifacts so a bad
    chunk can never reach the embedder.
    """
    text = html.unescape(text)              # &amp; -> & , &#39; -> '
    text = re.sub(r"<[^>]+>", "", text)     # drop any leftover HTML tags
    text = re.sub(r"[ \t]+\n", "\n", text)  # trailing whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)  # 3+ blank lines -> one blank line
    return text.strip()


def load_documents():
    """Load and clean every .txt document, parsing its metadata header."""
    documents = []
    for filename in sorted(os.listdir(DOCS_PATH)):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(DOCS_PATH, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            raw = f.read()

        meta, body = _parse_header(raw)
        documents.append({
            "filename": filename,
            "title": meta.get("title", filename.replace(".txt", "")),
            "source": meta.get("source") or meta.get("source_type", "unknown"),
            "program": meta.get("program", "unknown"),
            "url": meta.get("url", ""),
            "text": clean_text(body),
        })

    print(f"Loaded {len(documents)} document(s): "
          f"{[d['filename'] for d in documents]}")
    return documents


# ---------------------------------------------------------------------------
# Chunking — structure-aware, then token-bounded
# ---------------------------------------------------------------------------

def _split_by_tokens(text, max_tokens, overlap_tokens):
    """
    Sliding-window split for any single piece that exceeds the token budget.

    Only called on segments too long to stand alone (a long blog paragraph or
    a very long post). Shorter segments pass through untouched.

    We map each token window back to its character span and slice the ORIGINAL
    string, rather than decoding wordpieces — all-MiniLM-L6-v2's tokenizer is
    uncased and would otherwise return lowercased text with mangled spacing.
    """
    tok = _get_tokenizer()
    enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    offsets = enc["offset_mapping"]
    if len(offsets) <= max_tokens:
        return [text]

    pieces = []
    step = max_tokens - overlap_tokens
    for start in range(0, len(offsets), step):
        window = offsets[start:start + max_tokens]
        char_start = window[0][0]
        char_end = window[-1][1]
        piece = text[char_start:char_end].strip()
        if piece:
            pieces.append(piece)
        if start + max_tokens >= len(offsets):
            break
    return pieces


def _split_reddit(body):
    """
    Split a Reddit thread into its original post and each individual comment.

    Yields raw segment strings. Boundary markers ("Original Post:",
    "Comment N:") are stripped, but "User X:" attribution lines are kept so the
    chunk still shows who is speaking.
    """
    # Split right before each Original Post / Comment marker.
    parts = re.split(r"\n(?=Original Post:|Comment\s*\d*\s*:)", body)
    segments = []
    for part in parts:
        part = re.sub(r"^(Original Post:|Comment\s*\d*\s*:)\s*", "",
                      part.strip())
        part = part.strip()
        if part:
            segments.append(part)
    return segments


def _split_blog(body):
    """Split a blog post on blank-line paragraph boundaries."""
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    return paras


def _pack(segments, max_tokens, overlap_tokens, min_tokens):
    """
    Greedily pack consecutive segments into chunks up to max_tokens.

    A segment bigger than the budget on its own is token-window split. When a
    chunk is flushed, trailing segments up to overlap_tokens are carried into
    the next chunk so context survives the boundary. Original text is preserved
    for everything that fits without window-splitting.
    """
    chunks = []
    current = []
    current_tokens = 0

    def flush():
        nonlocal current, current_tokens
        if current:
            chunks.append("\n\n".join(current))
        current, current_tokens = [], 0

    for seg in segments:
        seg_tokens = count_tokens(seg)

        if seg_tokens > max_tokens:
            flush()
            chunks.extend(_split_by_tokens(seg, max_tokens, overlap_tokens))
            continue

        if current and current_tokens + seg_tokens > max_tokens:
            flush_chunk = "\n\n".join(current)
            chunks.append(flush_chunk)
            # paragraph-level overlap: carry trailing segments up to the budget
            carry, carry_tokens = [], 0
            for prev in reversed(current):
                t = count_tokens(prev)
                if carry_tokens + t <= overlap_tokens:
                    carry.insert(0, prev)
                    carry_tokens += t
                else:
                    break
            current, current_tokens = carry, carry_tokens

        current.append(seg)
        current_tokens += seg_tokens

    flush()
    return [c for c in chunks if count_tokens(c) >= min_tokens]


def chunk_document(doc):
    """
    Turn one loaded document into a list of chunk dicts.

    Reddit threads are split by post/comment; blog posts by paragraph. Both are
    then packed/window-split to ~CHUNK_MAX_TOKENS. For Reddit, the thread title
    is prepended to every chunk so a one-line comment ("Yes, but plan
    carefully") is still understandable on its own.

    Each chunk dict carries:
      text, title, source, program, url, filename, chunk_id, n_tokens
    """
    body = doc["text"]
    is_reddit = ("Original Post:" in body
                 or doc["filename"].lower().startswith("reddit"))

    if is_reddit:
        segments = _split_reddit(body)
    else:
        segments = _split_blog(body)

    packed = _pack(segments, CHUNK_MAX_TOKENS, CHUNK_OVERLAP_TOKENS,
                   CHUNK_MIN_TOKENS)

    prefix = doc["filename"].replace(".txt", "")
    chunks = []
    for i, text in enumerate(packed):
        if is_reddit and doc["title"]:
            text = f"Reddit thread: {doc['title']}\n\n{text}"
        chunks.append({
            "text": text,
            "title": doc["title"],
            "source": doc["source"],
            "program": doc["program"],
            "url": doc["url"],
            "filename": doc["filename"],
            "chunk_id": f"{prefix}_{i}",
            "n_tokens": count_tokens(text),
        })
    return chunks


def build_chunks():
    """Load every document and return the full list of chunks."""
    documents = load_documents()
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))
    return documents, all_chunks


# ---------------------------------------------------------------------------
# Inspection — run `python ingest.py` to verify chunks before embedding (M4)
# ---------------------------------------------------------------------------

def _inspect(documents, chunks, n_samples=5):
    total = len(chunks)
    print("\n" + "=" * 70)
    print(f"  CHUNK INSPECTION  —  {total} chunks from {len(documents)} documents")
    print("=" * 70)

    # Per-document counts — quick check that every source contributed.
    print("\nChunks per document:")
    for doc in documents:
        c = sum(1 for ch in chunks if ch["filename"] == doc["filename"])
        print(f"  {doc['filename']:<20} {c:>3} chunks   ({doc['program']})")

    # Token-size distribution — confirms we're near the ~256 target, not way
    # under (too small) or over (would be truncated by the embedder).
    sizes = [c["n_tokens"] for c in chunks]
    if sizes:
        print(f"\nToken sizes: min={min(sizes)}  "
              f"avg={sum(sizes) // len(sizes)}  max={max(sizes)}")

    # Sanity guardrails from the milestone checkpoint.
    if total < 50:
        print("\n  WARNING: < 50 chunks — chunks may be too large/coarse.")
    elif total > 2000:
        print("\n  WARNING: > 2000 chunks — chunks may be too small/noisy.")
    else:
        print(f"\n  OK: {total} chunks is within the healthy 50–2000 range.")

    # Print evenly-spaced sample chunks spanning the corpus.
    print("\n" + "-" * 70)
    print(f"  {n_samples} SAMPLE CHUNKS  (read each: is it self-contained?)")
    print("-" * 70)
    step = max(1, total // n_samples)
    for idx in range(0, total, step)[:n_samples]:
        ch = chunks[idx]
        print(f"\n[{ch['chunk_id']}]  source={ch['filename']}  "
              f"program={ch['program']}  tokens={ch['n_tokens']}")
        print("  " + ch["text"].replace("\n", "\n  "))

    print("\n" + "=" * 70)
    print("  If any sample is a fragment, HTML, or empty — fix before M4.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    docs, all_chunks = build_chunks()
    _inspect(docs, all_chunks)