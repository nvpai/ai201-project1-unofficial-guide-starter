"""
Milestone 5 — Gradio interface for the UT Austin Unofficial Guide.

Wires the pipeline together: on startup it ingests + embeds the documents (once),
then serves a UI where each question runs retrieve -> grounded generate and
returns an answer with the source documents it drew from.

    python app.py    ->    open http://localhost:7860
"""

import gradio as gr

from ingest import build_chunks
from retriever import embed_and_store, get_collection
from generator import answer_question


# ---------------------------------------------------------------------------
# Ingestion — runs once on startup
# ---------------------------------------------------------------------------

def run_ingestion():
    """
    Load + chunk documents and embed them into ChromaDB.

    Skipped if the store is already populated. To re-ingest after changing the
    chunking strategy, delete the ./chroma_db folder and restart.
    """
    collection = get_collection()
    if collection.count() > 0:
        print(f"Vector store already populated ({collection.count()} chunks). "
              "Skipping ingestion.")
        print("To re-ingest, delete the ./chroma_db folder and restart.")
        return

    print("Ingesting documents...")
    _documents, chunks = build_chunks()
    if chunks:
        embed_and_store(chunks)
        print(f"Ingestion complete. {len(chunks)} chunks stored.")
    else:
        print("\nNo chunks produced — check ingest.py and the documents/ folder.\n")


# ---------------------------------------------------------------------------
# Query handler — retrieve -> grounded generate -> (answer, sources)
# ---------------------------------------------------------------------------

def handle_query(question):
    if not question or not question.strip():
        return "Please enter a question.", ""
    result = answer_question(question)
    sources = "\n".join(f"• {s}" for s in result["sources"]) or "— (no sources used)"
    return result["answer"], sources


EXAMPLES = [
    "If I retake a course I passed, does the new grade replace the old one?",
    "How much does the program cost and how many courses are required?",
    "What is the typical weekly workload for a single course?",
    "How are courses graded and are exams proctored?",
    "Which courses do students commonly take or recommend?",
    "Is it realistic to finish the program quickly while working full-time?",
]


# ---------------------------------------------------------------------------
# Gradio UI  (Gradio 6 API: simple Blocks + Textbox/Button)
# ---------------------------------------------------------------------------

with gr.Blocks(title="UT Austin Unofficial Guide") as demo:
    gr.Markdown(
        "# 🤘 UT Austin Unofficial Guide\n"
        "Real student experiences of the online **MSCSO** & **MSDSO** programs — "
        "answers grounded in Reddit threads and student blogs. "
        "If the documents don't cover your question, the guide says so rather than guessing."
    )

    question = gr.Textbox(
        label="Your question",
        placeholder='e.g. "How much does the program cost and how many courses are required?"',
        lines=2,
    )
    ask_btn = gr.Button("Ask", variant="primary")

    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Grounded in these sources", lines=3)

    gr.Examples(examples=EXAMPLES, inputs=question)

    ask_btn.click(handle_query, inputs=question, outputs=[answer, sources])
    question.submit(handle_query, inputs=question, outputs=[answer, sources])


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  UT Austin Unofficial Guide — starting up")
    print("=" * 50 + "\n")
    run_ingestion()
    # theme moved to launch() in Gradio 6; burnt-orange to match UT Austin.
    demo.launch(theme=gr.themes.Soft(primary_hue="orange"))
