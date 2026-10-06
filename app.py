import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load my API key from the .env file so it never ends up in the repo
load_dotenv()

# --- Settings ---------------------------------------------------------------
PAPERS_DIR = Path("./papers_data")   # where I keep the PDFs
PERSIST_DIRECTORY = "./chroma_db"    # the vector database lives here
CHUNK_SIZE = 1000                    # characters per chunk
CHUNK_OVERLAP = 200                  # overlap so an idea cut at a boundary isn't lost
TOP_K = 3                            # how many chunks to pull per question
# check the current model name
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# I want the model to answer only from the papers, and to say so when the
# answer isn't there instead of making something up.
PROMPT_TEMPLATE = """You are a research assistant helping explore a corpus of scientific papers.
Answer the question using ONLY the context below. If the context does not
contain enough information, say so explicitly instead of guessing.

Context:
{context}

Question: {question}

Answer:"""


def build_vector_db(embeddings):
    """Build the vector database from scratch (only needed the first time)."""
    # Read every PDF in the folder. Each page becomes a document that keeps
    # its file name and page number, which I need later for the sources.
    print("Loading PDFs...")
    documents = PyPDFDirectoryLoader(str(PAPERS_DIR)).load()
    if not documents:
        raise SystemExit(
            f"No PDFs found in '{PAPERS_DIR}'. Add some papers there and run again!")

    # Whole pages are too big for precise retrieval, so I cut them into
    # smaller overlapping chunks.
    print(f"Loaded {len(documents)} pages. Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(documents)

    # Turn each chunk into an embedding (a vector that captures its meaning)
    # and save everything in Chroma.
    print(f"Creating embeddings for {len(chunks)} chunks...")
    return Chroma.from_documents(
        chunks, embeddings, persist_directory=PERSIST_DIRECTORY
    )


def load_vector_db(embeddings):
    """Open the existing database, or build it if it isn't there yet."""
    if Path(PERSIST_DIRECTORY).exists():
        # Already built, so just load it. No need to pay for embeddings again.
        return Chroma(
            persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings
        )
    # First run: make sure the papers folder exists, then build the database
    PAPERS_DIR.mkdir(exist_ok=True)
    return build_vector_db(embeddings)


def answer(question, retriever, llm):
    """Answer one question and return the answer plus the sources it used."""
    # 1. Find the chunks closest in meaning to the question
    docs = retriever.invoke(question)

    # 2. Glue them together into one block of context
    context = "\n\n---\n\n".join(d.page_content for d in docs)

    # 3. Put context and question into the prompt and ask the model
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    response = llm.invoke(prompt)

    # 4. Collect the unique (paper, page) pairs so I can check any claim
    #    against the original text
    sources = sorted(
        {
            (Path(d.metadata.get("source", "unknown")).name, d.metadata.get("page"))
            for d in docs
        },
        key=lambda s: (s[0], s[1] if s[1] is not None else -1),
    )
    return response.content, sources


def main():
    # Stop early with a clear message if the API key is missing
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key.")

    # Set up the pieces: embeddings, database, retriever and the model
    embeddings = OpenAIEmbeddings()
    db = load_vector_db(embeddings)
    retriever = db.as_retriever(search_kwargs={"k": TOP_K})
    # temperature 0: consistent answers, no creativity
    llm = ChatOpenAI(model=LLM_MODEL, temperature=0)

    print("\n--- RAG Assistant ready. Type 'exit' to quit. ---")
    while True:
        question = input("\nAsk something about your papers: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue  # just Enter? ask again

        text, sources = answer(question, retriever, llm)
        print(
            f"\nAnswer:\n{text}\n\nRetrieved passages (may not support the answer):")
        for name, page in sources:
            # PyPDF counts pages from 0, so I add 1 to match what you see in the PDF
            page_label = page + 1 if isinstance(page, int) else "N/A"
            print(f"- {name} (page {page_label})")


# Only run main() when I execute this file directly
if __name__ == "__main__":
    main()
