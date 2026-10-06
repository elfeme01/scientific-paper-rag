# Scientific Paper RAG Assistant

A command-line question-answering tool over a local corpus of scientific papers (PDFs). I built it to support the literature exploration phase of a systematic review on the limits of intelligent automation.

Every answer is accompanied by the papers and pages that were retrieved, so claims can be checked against the original text.

> **Scope note:** this tool helps explore and navigate a literature corpus. It does not replace the screening and inclusion process of a systematic review, and its answers should always be verified against the sources.

## How it works

```
PDFs → chunks → embeddings → Chroma vector DB → top-3 retrieval → LLM → answer + retrieved pages
```

| Step | Choice | Notes |
|---|---|---|
| Loading | `PyPDFDirectoryLoader` | One document per PDF page, keeping file name and page number as metadata |
| Chunking | `RecursiveCharacterTextSplitter`, 1000 characters, 200 overlap | Overlap so an idea cut at a boundary is not lost |
| Embeddings | OpenAI embeddings via `langchain-openai` | |
| Vector store | Chroma, persisted locally | Built on first run, reused afterwards |
| Retrieval | Top-3 chunks | |
| Generation | `gpt-4o-mini` by default (configurable via `LLM_MODEL`), temperature 0 | Prompt restricts the model to the retrieved context and asks it to say so when the answer is not there |

In my corpus, 2 papers (23 pages) became 150 chunks.

## Setup

Requires Python 3 and an OpenAI API key.

```bash
git clone https://github.com/elfeme01/scientific-paper-rag.git
cd scientific-paper-rag
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1   |   macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file from the template and add your key:

```bash
# Windows PowerShell: Copy-Item .env.example .env
cp .env.example .env
```

Put your PDFs in `papers_data/` (the PDFs I used are not included for copyright reasons; see [`papers_list.md`](papers_list.md)), then run:

```bash
python app.py
```

On first run the vector database is built from the PDFs (this calls the OpenAI embeddings API, so it has a small cost). Later runs reuse it. If you change the PDFs, delete `chroma_db/` so it is rebuilt.

## Example

```
Ask something about your papers: What are the five core components of the proposed ML-DevOps architecture?

Answer:
The five core components of the proposed ML-DevOps architecture are: (i) Predictive Analytics Engine, (ii) Anomaly Detection System, (iii) Reinforcement Learning Agent (RLA), (iv) Resource Optimizer (RO), and (v) Integration and Orchestration Layer.

Retrieved passages (may not support the answer):
- Dileep Kumar and Mathew - 2026 - ML ‐Driven DevO.PDF (page 2)
- Dileep Kumar and Mathew - 2026 - ML ‐Driven DevO.PDF (page 4)
- Dileep Kumar and Mathew - 2026 - ML ‐Driven DevO.PDF (page 5)
```

Page numbers are positions in the PDF, which can differ from the page numbers printed in the journal.

## Evaluation

I ran a small sanity check on 7 questions over the 2-paper corpus (top-3 retrieval): single-paper lookups, a question spanning both papers, an out-of-scope question, and a question in Greek over English papers. I checked each answer and its cited pages against the PDFs. All 7 answers were judged correct, including two cases where the system correctly said the context did not contain the answer, and the retrieved pages supported the answer in all 5 questions where it gave one.

Full table: [`evaluation/results.md`](evaluation/results.md).

**Caveats**
- 7 questions on 2 papers is a sanity check, not a benchmark. It says little about performance on a larger corpus.
- I wrote the questions myself and checked the answers after running the system, so they may be easier than real use.
- In the cross-paper question, retrieval returned 2 chunks from one paper and 1 from the other. With a fixed top-3, multi-paper questions can be unbalanced.
- The "Retrieved passages" list shows what retrieval returned, not necessarily what supports the answer. It is also shown when the system refuses.

## Limitations and next steps

- Fixed top-k retrieval; questions that need synthesis across many papers are likely to be weak.
- No automated evaluation; the check above is manual and small.
- Behaviour with tables, figures and equations in PDFs has not been tested.
- The corpus is small (2 papers), so retrieval quality at scale is untested.
- Next steps: a larger evaluation set, comparing different `k` values and chunk sizes, metadata filtering by paper, and an interface beyond the command line.

## Tech stack

Python · LangChain · ChromaDB · OpenAI API · pypdf