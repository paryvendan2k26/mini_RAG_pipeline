import json
import re
from pathlib import Path


def slugify(value: str) -> str:
    slug = value.lower().replace(" ", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def load_documents(kb_dir: str | Path) -> list[dict[str, str]]:
    kb_path = Path(kb_dir)
    documents: list[dict[str, str]] = []

    for file_path in sorted(kb_path.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if len(lines) < 3:
            raise ValueError(f"Document header is incomplete: {file_path}")

        title_line = lines[0]
        section_line = lines[1]
        if not title_line.startswith("Title: ") or not section_line.startswith("Section: "):
            raise ValueError(f"Document header is invalid: {file_path}")

        try:
            blank_index = lines.index("")
        except ValueError as exc:
            raise ValueError(f"Document body separator is missing: {file_path}") from exc

        body = "\n".join(lines[blank_index + 1 :]).strip()
        documents.append(
            {
                "doc_title": title_line.removeprefix("Title: ").strip(),
                "section": section_line.removeprefix("Section: ").strip(),
                "body": body,
                "source_file": str(file_path),
            }
        )

    return documents


def chunk_sentences(document: dict[str, str]) -> list[dict[str, object]]:
    body = document["body"]
    chunks: list[dict[str, object]] = []
    slug = slugify(document["doc_title"])

    matches = re.finditer(r"[^.\n]+", body)
    for sentence_index, match in enumerate(matches):
        text = match.group(0).strip()
        if not text:
            continue

        chunks.append(
            {
                "chunk_id": f"{slug}_s{sentence_index}",
                "doc_title": document["doc_title"],
                "section": document["section"],
                "text": text,
                "start_char": match.start(),
                "end_char": match.end(),
                "strategy": "sentence",
            }
        )

    return chunks


def chunk_fixed(document: dict[str, str], max_chars: int = 200, overlap: int = 20) -> list[dict[str, object]]:
    if overlap >= max_chars:
        raise ValueError("overlap must be smaller than max_chars")

    body = document["body"]
    chunks: list[dict[str, object]] = []
    slug = slugify(document["doc_title"])
    start = 0
    chunk_index = 0

    while start < len(body):
        end = min(start + max_chars, len(body))
        text = body[start:end].strip()
        if text:
            chunks.append(
                {
                    "chunk_id": f"{slug}_c{chunk_index}",
                    "doc_title": document["doc_title"],
                    "section": document["section"],
                    "text": text,
                    "start_char": start,
                    "end_char": end,
                    "strategy": "fixed",
                }
            )
            chunk_index += 1

        if end == len(body):
            break
        start = end - overlap

    return chunks


def chunk_documents(documents: list[dict[str, str]], strategy: str = "sentence") -> list[dict[str, object]]:
    chunks: list[dict[str, object]] = []
    for document in documents:
        if strategy == "sentence":
            chunks.extend(chunk_sentences(document))
        elif strategy == "fixed":
            chunks.extend(chunk_fixed(document))
        else:
            raise ValueError(f"Unsupported chunking strategy: {strategy}")
    return chunks


def run_ingestion(kb_dir: str | Path, strategy: str = "sentence") -> list[dict[str, object]]:
    documents = load_documents(kb_dir)
    chunks = chunk_documents(documents, strategy=strategy)

    artifacts_dir = Path("artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    chunks_path = artifacts_dir / "chunks.json"
    chunks_path.write_text(json.dumps(chunks, indent=2), encoding="utf-8")

    print(f"Loaded {len(documents)} documents")
    print(f"Created {len(chunks)} chunks")
    return chunks
