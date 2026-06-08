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
| 1 | Medium (Blog)| Student's blog on his journey with UTAustin's MSCSO program  | https://medium.com/@sudz24/my-journey-with-ut-austins-mcso-a21d70a150c6|

| 2 | Student Personal Blog | Student review on UT Austin MSDS Online program| https://modalshift.co/msdso-review/|
| 3 | Student Personal Blog | Experience of a master’s in computer science (online) at UT Austin
 | https://921kiyo.com/ut-austin-cs-online/ |
| 4 | Reddit - r/MSCSO | UT Austin MS-DS with a Full-Time Job?  | https://www.reddit.com/r/MSCSO/comments/1t15ncr/ut_austin_msds_with_a_fulltime_job/ |
| 5 | Reddit - r/MSCSO  | Fail a course or final exam, do you have to repay for the whole class?| https://www.reddit.com/r/MSCSO/comments/1ttz0oq/if_you_fail_a_course_or_final_exam_do_you_have_to/|
| 6 | Reddit - r/MSCSO | What is your typically weekly workload?
Reddit| https://www.reddit.com/r/MSCSO/comments/1svkt9g/what_is_your_typically_weekly_workload/ |
| 7 | Reddit - r/MSCSO | Questions about newly admitted candidate to UT Austin MSCSO | https://www.reddit.com/r/MSCSO/comments/1ss1oed/questions_about_newly_admitted_candidate_to_ut/ |
| 8 | Reddit - r/MSCSO  | Retaking course opinions | https://www.reddit.com/r/MSCSO/comments/1shxv1i/retaking_course_opinions/ |
| 9 | Reddit - r/MSCSO | Grading Breakdown & Exam Proctoring  | https://www.reddit.com/r/MSCSO/comments/1sdruu2/msdso_course_format_question_grading_breakdown/|
| 10 | Reddit - r/MSCSO | Possible to finish the course in 1.5 years? | https://www.reddit.com/r/MSCSO/comments/1s62mx7/possible_to_finish_in_15_years/|

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
500
**Overlap:**
100
**Reasoning:**
I will use a chunk size of 500 tokens with an overlap of 100 tokens. This size is large enough to capture complete thoughts about topics such as workload, course quality, and student experiences, while remaining small enough for accurate retrieval.
Reddit threads will be split into the original post and comments, while blog posts will be chunked by their section headings. The 100-token overlap helps preserve context when information spans multiple chunks.


---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

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
