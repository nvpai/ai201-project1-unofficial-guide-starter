"""
Milestone 5 — Grounded answer generation.

Pipeline stage [5] from planning.md:

    GENERATION
    Groq + llama-3.3-70b-versatile
    (Answer ONLY from retrieved chunks, with source citations)

Grounding is enforced two ways, not just suggested:
  1. A strict system prompt that forbids outside knowledge and mandates an
     exact "I don't have enough information" reply when the context is silent.
  2. A relevance gate: chunks looser than MAX_CONTEXT_DISTANCE are dropped, and
     if nothing relevant survives we decline *before* calling the LLM.
Source attribution is added programmatically from chunk metadata, so it can't
be hallucinated or omitted by the model.

Run `python generator.py` to test end-to-end (needs network + a GROQ_API_KEY).
"""

from groq import Groq

from config import GROQ_API_KEY, LLM_MODEL
from retriever import retrieve

_client = Groq(api_key=GROQ_API_KEY)

# Chunks looser than this cosine distance are treated as irrelevant and kept
# out of the context. In Milestone 4 testing, real answers scored 0.20-0.49 and
# weak/adjacent matches 0.54-0.58, so 0.8 only filters clearly-unrelated chunks
# (e.g. off-domain questions) while leaving genuine matches intact.
MAX_CONTEXT_DISTANCE = 0.8

# Exact text the model must use when the context can't answer the question.
NO_ANSWER = "I don't have enough information on that in the documents I have."

SYSTEM_PROMPT = f"""You are the "UT Austin Unofficial Guide" assistant. You answer \
questions about UT Austin's online master's programs (MSCSO and MSDSO) using ONLY \
the student reviews, blog posts, and Reddit discussions supplied to you as context.

Rules:
- Answer using ONLY the information in the provided context documents. Do NOT use \
any outside or prior knowledge, and do NOT add general advice.
- If the context does not contain enough information to answer, reply with EXACTLY \
this sentence and nothing else: "{NO_ANSWER}"
- Do not guess or infer beyond what the text says.
- Keep the answer concise and specific to what students actually reported.
- If sources disagree, note the disagreement rather than picking one.
- These are student opinions, not official policy — phrase answers as what \
students say/report."""


def _format_context(chunks):
    """Render surviving chunks into a numbered context block for the prompt."""
    blocks = []
    for i, c in enumerate(chunks, 1):
        label = c.get("title") or c.get("source")
        blocks.append(
            f"[{i}] (source: {c['source']} — {label} · {c['program']})\n{c['text']}"
        )
    return "\n\n".join(blocks)


def _source_list(chunks):
    """Unique source documents (filename + url) for programmatic attribution."""
    sources, seen = [], set()
    for c in chunks:
        if c["source"] in seen:
            continue
        seen.add(c["source"])
        entry = c["source"]
        if c.get("url"):
            entry += f" — {c['url']}"
        sources.append(entry)
    return sources


def answer_question(query, n_results=None):
    """
    Full retrieve -> generate flow. Returns a dict:
      answer  : grounded answer string (or the NO_ANSWER sentence)
      sources : list of source documents the answer is grounded in (may be empty)
    """
    hits = retrieve(query) if n_results is None else retrieve(query, n_results)
    relevant = [h for h in hits if h.get("distance", 1.0) <= MAX_CONTEXT_DISTANCE]

    # Relevance gate: nothing on-topic -> decline without calling the LLM.
    if not relevant:
        return {"answer": NO_ANSWER, "sources": []}

    user_prompt = (
        f"Context documents:\n\n{_format_context(relevant)}\n\n"
        f"Question: {query}\n\n"
        "Answer the question using only the context above."
    )

    completion = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,   # low temperature keeps the answer close to the text
    )
    answer = completion.choices[0].message.content.strip()

    # If the model declined, don't attach sources (nothing was actually used).
    sources = [] if answer.startswith(NO_ANSWER[:25]) else _source_list(relevant)
    return {"answer": answer, "sources": sources}


def generate_response(query, retrieved_chunks=None):
    """
    Convenience wrapper returning a single formatted string (answer + sources),
    used by the Gradio chat interface in app.py.

    `retrieved_chunks` is accepted for backwards compatibility; when provided it
    is used directly instead of re-retrieving.
    """
    if retrieved_chunks is None:
        result = answer_question(query)
    else:
        relevant = [c for c in retrieved_chunks
                    if c.get("distance", 1.0) <= MAX_CONTEXT_DISTANCE]
        if not relevant:
            return NO_ANSWER
        user_prompt = (
            f"Context documents:\n\n{_format_context(relevant)}\n\n"
            f"Question: {query}\n\nAnswer the question using only the context above."
        )
        completion = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
        answer = completion.choices[0].message.content.strip()
        sources = [] if answer.startswith(NO_ANSWER[:25]) else _source_list(relevant)
        result = {"answer": answer, "sources": sources}

    if not result["sources"]:
        return result["answer"]
    src = "\n".join(f"• {s}" for s in result["sources"])
    return f"{result['answer']}\n\n---\n**Sources:**\n{src}"


if __name__ == "__main__":
    # End-to-end grounding test: 2 in-domain questions + 1 off-domain question.
    tests = [
        "How are courses graded and are exams proctored?",   # in-domain
        "How much does the program cost?",                    # in-domain
        "What's the weather like in Austin this weekend?",    # off-domain -> decline
    ]
    for q in tests:
        print("\n" + "=" * 74)
        print(f"Q: {q}")
        print("-" * 74)
        res = answer_question(q)
        print(res["answer"])
        if res["sources"]:
            print("\nSources:")
            for s in res["sources"]:
                print(f"  • {s}")
    print("\n" + "=" * 74)