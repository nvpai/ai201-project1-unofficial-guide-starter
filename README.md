# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
My system covers student reviews and experiences of UT Austin's Online Master's programs, specifically the Master of Science in Computer Science Online (MSCSO) and Master of Science in Data Science Online (MSDSO). It focuses on student-generated insights about coursework, workload, instructor quality, program flexibility, difficulty, and career outcomes gathered from Reddit discussions, blogs, and other online communities.
Official program websites provide information about admissions, degree requirements, and course offerings, but they do not reflect students' real experiences with workload, course difficulty, instructor quality, time commitment, and career outcomes.
---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Medium (Blog)| Text Blog| https://medium.com/@sudz24/my-journey-with-ut-austins-mcso-a21d70a150c6|
| 2 | Student Personal Blog | Text Blog| https://modalshift.co/msdso-review/|
| 3 | Student Personal Blog | Text Blog | https://921kiyo.com/ut-austin-cs-online/ |
| 4 | Reddit - r/MSCSO | Text Reddit  | https://www.reddit.com/r/MSCSO/comments/1t15ncr/ut_austin_msds_with_a_fulltime_job/ |
| 5 | Reddit - r/MSCSO  | Text Reddit | https://www.reddit.com/r/MSCSO/comments/1ttz0oq/if_you_fail_a_course_or_final_exam_do_you_have_to/|
| 6 | Reddit - r/MSCSO |Text Reddit  | https://www.reddit.com/r/MSCSO/comments/1svkt9g/what_is_your_typically_weekly_workload/ |
| 7 | Reddit - r/MSCSO | Text Reddit  | https://www.reddit.com/r/MSCSO/comments/1ss1oed/questions_about_newly_admitted_candidate_to_ut/ |
| 8 | Reddit - r/MSCSO  | Text Reddit  | https://www.reddit.com/r/MSCSO/comments/1shxv1i/retaking_course_opinions/ |
| 9 | Reddit - r/MSCSO |  Text Reddit  | https://www.reddit.com/r/MSCSO/comments/1sdruu2/msdso_course_format_question_grading_breakdown/|
| 10 | Reddit - r/MSCSO | Text Reddit  | https://www.reddit.com/r/MSCSO/comments/1s62mx7/possible_to_finish_in_15_years/|

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**
A maximum of ~256 tokens per chunk. I originally planned 500 tokens, but my embedding model `all-MiniLM-L6-v2` truncates any input longer than 256 tokens — so a 500-token chunk would only be half "seen" during similarity search, hurting retrieval. I lowered the cap to 256 so the entire chunk influences the embedding. Most student comments and blog paragraphs fit comfortably under this limit (final corpus averages ~192 tokens per chunk).

**Overlap:**
50 tokens (~20%). Because I chunk on natural boundaries (individual Reddit comments, blog paragraphs), most chunks are already self-contained and overlap only matters when a long passage has to be split. 50 tokens preserves context across those cuts without heavily duplicating content. (At a 256-token cap, the originally planned 100-token overlap would have meant ~40% duplication, which is wasteful.)

**Why these choices fit your documents:**
I used a **structure-aware** approach (see `ingest.py`) rather than a blind fixed-size split, because my corpus has two very different shapes:
- **Reddit threads** are split into the original post and each individual comment, and the thread title is prepended to every chunk so a short reply (e.g. "Yes, but plan carefully") is still understandable on its own.
- **Blog posts** are split on paragraph boundaries and greedily packed up to the 256-token budget.
- Any single segment longer than 256 tokens is sliding-window split using the real `all-MiniLM-L6-v2` tokenizer's **character offsets**, so original casing and spacing are preserved (decoding wordpieces would have lowercased the text).

This keeps each chunk a complete, retrievable thought, which the Milestone 4 retrieval test confirmed (relevant chunks returned with cosine distances of 0.20–0.49).

**Preprocessing before chunking:**
Each document begins with a metadata header (`title:`, `source:`, `url:`, `program:`) that I parse out and store as chunk metadata for source attribution rather than leaving it in the chunk text. I also unescape HTML entities, strip any stray HTML tags, and collapse runs of blank lines so no boilerplate or markup reaches the embedder.

**Final chunk count:**
53 chunks across 10 documents (within the healthy 50–2,000 range).
---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
`all-MiniLM-L6-v2` (sentence-transformers). It runs locally with no API key or rate limits, is free, and maps text to 384-dim vectors with good quality on short passages. Its 256-token input limit also set my chunk-size cap.

**Production tradeoff reflection:**
If cost weren't a constraint, I'd switch to a larger API model such as OpenAI `text-embedding-3-large` for better semantic accuracy on domain-specific text and a longer context window (so I wouldn't need a 256-token cap). My corpus is English-only, so multilingual support doesn't matter here. The trade-off is added latency, per-call cost, and an external API dependency in exchange for stronger retrieval.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
The system prompt (in `generator.py`) instructs the model to *"Answer using ONLY the information in the provided context documents. Do NOT use any outside or prior knowledge"* and, when the context can't answer, to reply with the exact sentence *"I don't have enough information on that in the documents I have."* Retrieved chunks are passed in a numbered context block, and `temperature=0.1` keeps the answer close to the text. A structural safeguard backs this up: chunks with cosine distance > 0.8 are filtered out, and if none survive the system declines *before* calling the LLM — so off-domain questions are refused programmatically, not just by trusting the prompt.

**How source attribution is surfaced in the response:**
Sources are added **programmatically** from each retrieved chunk's metadata (source filename + URL), not generated by the LLM, so a citation can't be hallucinated or omitted. The UI shows them in a separate "Grounded in these sources" box, and when the model declines no sources are attached.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | If I retake a course I already passed, does the new grade replace the old one? | No — retaking averages with the old grade, it doesn't replace it. | "Retaking a class will not replace the previous grade, it will just average with it." Correct source `reddit8.txt` retrieved at rank 2 (dist 0.46). | Relevant | Accurate |
| 2 | How much does the program cost, how many courses are required, and how long to complete? | $1,000/course × 10 = $10,000 (+$125/sem intl fee); up to 6 years to finish. | Correctly gave $1,000/course, $10,000 total, 10 courses — but said the completion time was "not explicitly stated," missing the "up to 6 years" fact. | Partially relevant | Partially accurate |
| 3 | What is the typical weekly workload for a single course? | ~8–20 hrs/week depending on difficulty. | "8 to 20 hours per week depending on difficulty," with the AOS+DL (<10 hrs) and GIOS+DL (15–20 hrs) examples. | Relevant | Accurate |
| 4 | How are courses graded and assessed, and are exams proctored? | Varies by course; mix of assignments/projects/exams/quizzes; some proctored (ML by recording), some honor-code; DL unproctored; no in-person/live proctoring. | Detailed and correct: project-based vs. mixed courses, MCQ + descriptive exams, ML recorded-proctored, DL unproctored, honor code. Top result dist 0.20. | Relevant | Accurate |
| 5 | Which courses do MSCSO/MSDSO students commonly take or recommend? | DL, NLP, Data Structures & Algorithms, ML, RL, etc. | Failed: said "specific courses are not mentioned" and pointed to MSDS Hub / program overlap instead of naming courses. Retrieval pulled meta-discussion chunks, not the per-course review chunks. | Off-target | Inaccurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

**Summary:** 3/5 accurate (Q1, Q3, Q4), 1 partially accurate (Q2), 1 inaccurate (Q5). Accuracy tracked retrieval quality closely — the two weaker answers came from retrieval pulling the wrong or incomplete chunks, not from the LLM ignoring the context.

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
Q5 — "Which courses do MSCSO/MSDSO students commonly take or recommend?"

**What the system returned:**
It said "specific courses are not mentioned" and pointed the user to the MSDS Hub website. But the documents clearly do name courses (Deep Learning, NLP, Data Structures & Algorithms, ML, Reinforcement Learning), so this answer was wrong.

**Root cause (tied to a specific pipeline stage):**
This was a **retrieval** problem, not a generation one. Each course is described in its own separate chunk (one chunk per course review), so no single chunk looks like a list of "recommended courses." When I asked the general question "which courses do students recommend," the search instead picked the chunks that *talk about choosing courses in general* (program overlap, "check MSDS Hub"). Those matched the wording of my question better. Since I only retrieve the top 3 chunks, the chunks that actually name the courses never reached the LLM — so the model had nothing to list and correctly refused to make courses up.

**What you would change to fix it:**
- Retrieve more chunks (raise top-k from 3 to about 6–8) so the per-course chunks have a chance to be included.
- Add the blog/section title to each course chunk (the same trick I already use for Reddit) so a "which courses" question matches them.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
Writing the planning.md first made me think carefully about the domain before any code. It pushed me to collect enough documents to actually cover the topic, to decide on a chunking strategy that fit those documents, and to write evaluation questions based on what the documents really contained. By the time I started coding, I already knew what data I had and what the system needed to answer, so building each stage was much smoother.

**One way your implementation diverged from the spec, and why:**
My spec planned a chunk size of 500 tokens, but during implementation I lowered it to ~256 tokens. I found that my embedding model, `all-MiniLM-L6-v2`, only reads the first 256 tokens of any input and ignores the rest. A 500-token chunk would have been half-ignored during search, hurting retrieval, so I capped chunks at 256 tokens (and reduced overlap from 100 to 50 to match) and updated planning.md to reflect the change.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1 — Embedding model and chunk size**

- *What I gave the AI:* My plan to use 500-token chunks with the `all-MiniLM-L6-v2` embedding model.
- *What it produced:* It pointed out that this model only reads the first 256 tokens of any input and ignores the rest, so a 500-token chunk would be half-ignored during search.
- *What I changed or overrode:* I lowered the chunk-size cap from 500 to 256 tokens (and reduced overlap from 100 to 50 to match) so that the whole chunk is actually used during retrieval, and I updated planning.md to record the change and the reason.

**Instance 2 — Evaluation questions**

- *What I gave the AI:* My 5 draft evaluation questions and the actual documents, and asked it to make sure each question had a specific, checkable answer.
- *What it produced:* A review that flagged "Is the MSCSO worth it?" as too subjective to grade — there was no single correct answer to check against.
- *What I changed or overrode:* I replaced that question with a factual one about cost, number of courses, and completion time, which has a verifiable answer. I kept my other four questions but tightened their expected answers to point at the exact source documents.
