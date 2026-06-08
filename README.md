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
I used a chunk size of 500 tokens. This size works well for my project because most documents contain student experiences and opinions that can be captured within a few paragraphs.
**Overlap:**
Overlap of 100. The overlap helps preserve context when important information spans multiple chunks.
**Why these choices fit your documents:**
I will use a chunk size of 500 tokens with an overlap of 100 tokens. This size is large enough to capture complete thoughts about topics such as workload, course quality, and student experiences, while remaining small enough for accurate retrieval.
Reddit threads will be split into the original post and comments, while blog posts will be chunked by their section headings. The 100-token overlap helps preserve context when information spans multiple chunks.

**Final chunk count:**


---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

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

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
