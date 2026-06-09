# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

---
For this project, I selected the domain "Student Perspectives on UT Austin's Online Master's Programs (MSCSO and MSDSO)." The focus is on collecting and organizing experiences shared by students who have enrolled in or completed these programs, including their opinions on coursework, instructors, workload, flexibility, and career impact.
This type of information is useful because students considering these programs often have questions that go beyond the details available on official university pages. While university website provides information about admissions, curriculum, and program structure, it does not capture the day-to-day realities of being a student in the program. Insights about managing coursework while working full-time, which classes are particularly challenging, and whether graduates felt the degree met their expectations are typically found in Reddit discussions, blogs, and online communities. Since these experiences are spread across many different sources, they can be difficult to discover and compare, making them a good fit for this project.

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Medium (Blog) | Student's blog on his journey with UT Austin's MSCSO program | https://medium.com/@sudz24/my-journey-with-ut-austins-mcso-a21d70a150c6 |
| 2 | Student Personal Blog | Student review on UT Austin MSDS Online program | https://modalshift.co/msdso-review/ |
| 3 | Student Personal Blog | Experience of a master's in computer science (online) at UT Austin | https://921kiyo.com/ut-austin-cs-online/ |
| 4 | Reddit - r/MSCSO | UT Austin MS-DS with a Full-Time Job? | https://www.reddit.com/r/MSCSO/comments/1t15ncr/ut_austin_msds_with_a_fulltime_job/ |
| 5 | Reddit - r/MSCSO | Fail a course or final exam, do you have to repay for the whole class? | https://www.reddit.com/r/MSCSO/comments/1ttz0oq/if_you_fail_a_course_or_final_exam_do_you_have_to/ |
| 6 | Reddit - r/MSCSO | What is your typically weekly workload? | https://www.reddit.com/r/MSCSO/comments/1svkt9g/what_is_your_typically_weekly_workload/ |
| 7 | Reddit - r/MSCSO | Questions about newly admitted candidate to UT Austin MSCSO | https://www.reddit.com/r/MSCSO/comments/1ss1oed/questions_about_newly_admitted_candidate_to_ut/ |
| 8 | Reddit - r/MSCSO | Retaking course opinions | https://www.reddit.com/r/MSCSO/comments/1shxv1i/retaking_course_opinions/ |
| 9 | Reddit - r/MSCSO | Grading Breakdown & Exam Proctoring | https://www.reddit.com/r/MSCSO/comments/1sdruu2/msdso_course_format_question_grading_breakdown/ |
| 10 | Reddit - r/MSCSO | Possible to finish the course in 1.5 years? | https://www.reddit.com/r/MSCSO/comments/1s62mx7/possible_to_finish_in_15_years/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
~256 tokens (max). I originally planned 500 tokens, but the embedding model
`all-MiniLM-L6-v2` truncates any input longer than **256 tokens**, so a
500-token chunk would only be half-"seen" during similarity search. I lowered
the cap to 256 tokens so the whole chunk influences retrieval. Student
discussion text is dense — a single Reddit comment or blog paragraph usually
fits well under this limit (final corpus: avg ~192 tokens/chunk).

**Overlap:**
50 tokens (~20%). Because the chunker splits on natural boundaries
(comments, paragraphs), most chunks are already self-contained and overlap
only matters when a long passage has to be window-split. 50 tokens preserves
context across those cuts without heavily duplicating content.

**Reasoning:**
I used a **structure-aware** approach (implemented in `ingest.py`):
- **Reddit threads** are split into the original post and each individual
  comment, and the thread title is prepended to every chunk so a short reply
  ("Yes, but plan carefully") is still understandable on its own.
- **Blog posts** are split on paragraph boundaries and greedily packed up to
  the token budget.
- Any single segment longer than 256 tokens is sliding-window split using the
  real `all-MiniLM-L6-v2` tokenizer's **character offsets** (so original casing
  and spacing are preserved, not lowercased wordpieces).

This preserves complete thoughts and student experiences, producing more
meaningful chunks than a blind fixed-size split.

**Final chunk count:** 53 chunks across 10 documents (within the healthy
50–2000 range; per-document and token-size stats printed by `python ingest.py`).
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
`all-MiniLM-L6-v2`
A lightweight sentence-transformers model that runs locally with no API key or rate limits. It maps text to 384-dimensional vectors and provides good performance on short to medium passages. The tradeoff is slightly lower retrieval accuracy compared to larger commercial models, but it is fast, free, and easy to use for a course project.



**Top-k:**
I will use top 3 most relevant chunks for each query, which provides sufficient context while minimizing irrelevant results.

**Production tradeoff reflection:**
If I were deploying this system for real users and cost was not a constraint, I would prioritize retrieval accuracy over model size. Since the corpus consists of English-language student reviews, blogs, and Reddit discussions, multilingual support would be less important than accurately capturing the meaning of long-form student experiences. I would consider larger embedding models such as OpenAI's text-embedding-3-large, which may provide better semantic understanding and retrieval quality. The tradeoff would be higher latency and computational requirements, but these costs could be justified by more accurate and relevant search results.
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer | Grounding source(s) |
|---|----------|-----------------|---------------------|
| 1 | If I retake a course I already passed (e.g., to get a higher grade or digital badge), does the new grade replace the old one? | No. Retaking a class does **not** replace the previous grade — it just averages with it. Students also note a single C is fine as long as your GPA stays above 3.0, and that digital badges "do not matter at all" since employers generally don't care what grade you got in a specific course. | `reddit8.txt` (Retaking course opinions) |
| 2 | How much does the UT Austin online program cost, how many courses are required, and how long do you have to complete it? | The program requires **10 courses** at **$1,000 per course**, totaling **$10,000**. International students pay an additional **$125 per semester** international fee (introduced Fall '21). Students have up to **6 years** to complete the program. (For comparison, the blogs note Georgia Tech's OMSCS costs $540/course, ~$5,400 total.) | `blogMedium.txt`, `personalBlog2.txt` (modalshift), `PersonalBlog.txt` (kiyo) |
| 3 | What is the typical weekly workload for a single course? | A course's workload is roughly **8 to 20 hours per week** depending on its difficulty. Students give concrete examples — e.g., one reports AOS + DL totaling under 10 hours/week combined, while a coworker found GIOS and DL each took 15–20 hours. To stay under ~20–25 hours/week, students who take two courses usually pair an easy course with a medium one. | `blogMedium.txt`, `reddit6.txt` |
| 4 | How are courses typically graded and assessed, and are exams proctored? | Grading varies widely by course — usually a mix of assignments/programming, projects, quizzes, and exams (often a midterm and final), with some courses being entirely project-based or homework-only. Exams are a mix of MCQs and descriptive/theory questions; some are proctored and some rely on the honor code. Proctoring also varies: e.g., Deep Learning is unproctored with auto-graded assignments, while Machine Learning is proctored by recording (not live) for exams. No courses use live proctoring or in-person exams. Theory homework/exams can be submitted in LaTeX or handwritten. | `reddit9.txt`, `blogMedium.txt`, `PersonalBlog.txt` |
| 5 | Which courses do MSCSO/MSDSO students commonly take or recommend? | Frequently mentioned courses include Deep Learning, Natural Language Processing (highly praised, taught by Dr. Durrett), Data Structures & Algorithms, Machine Learning, Reinforcement Learning, Advanced Operating Systems, Parallel Systems, Data Exploration & Visualization, and Probability/Predictive Modeling courses. UT Austin is noted for a strong selection of ML-related courses (ML, RL, DL, Optimization, NLP, Advanced Linear Algebra). | `personalBlog2.txt`, `PersonalBlog.txt`, `blogMedium.txt` |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
## Architecture
    

 The UT Austin Online Master's Guide is a RAG (Retrieval-Augmented Generation) pipeline with five components:

## Architecture

```text
User Query
    │
    ▼
[1] DOCUMENT INGESTION
    Python 
    (Load and clean Reddit threads and blog posts)
    │
    ▼
[2] CHUNKING
    Structure-aware splitter (ingest.py)
    (Reddit: post + each comment; Blog: paragraphs)
    (~256 tokens max, 50 overlap — capped to embedder limit)
    │
    ▼
[3] EMBEDDING + VECTOR STORE
    all-MiniLM-L6-v2
    +
    ChromaDB
    (Generate embeddings and store vectors)
    │
    ▼
[4] RETRIEVAL
    ChromaDB Similarity Search
    (Top-k = 3)
    │
    ▼
[5] GENERATION
    Groq + llama-3.3-70b-versatile
    (Generate grounded answers using retrieved chunks)
    │
    ▼
Response with Source Citations
```

**Tools Used**

* **Ingestion:** Python (plain-text loader + header/metadata parsing in `ingest.py`)
* **Chunking:** Structure-aware (Reddit comments and blog paragraphs), ~256-token cap, 50 overlap
* **Embeddings:** `all-MiniLM-L6-v2`
* **Vector Store:** ChromaDB
* **Retrieval:** Similarity search (`top-k = 3`)
* **Generation:** llama-3.3-70b-versatile
* **UI:** Gradio





---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
