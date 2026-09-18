import json
import math
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

from langchain_aws import BedrockEmbeddings

from app.core.settings import get_settings
from app.services.crawler.service import CrawledPage, StructuredSegment


@dataclass
class RetrievedChunk:
    citation_id: str
    url: str
    title: str | None
    snippet: str
    content: str
    score: float
    semantic_score: float
    lexical_score: float
    rerank_score: float
    metadata: dict[str, str | int]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _scope_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower()


class IncrementalEmbeddingIndex:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.db_path = self._resolve_sqlite_path(self.settings.database_url)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._embeddings = BedrockEmbeddings(
            model_id=self.settings.embedding_model_id,
            region_name=self.settings.aws_region,
        )
        self._ensure_schema()

    def _resolve_sqlite_path(self, database_url: str) -> Path:
        prefix = "sqlite:///"
        if not database_url.startswith(prefix):
            raise ValueError("Only sqlite DATABASE_URL is supported in this prototype.")

        raw_path = database_url.replace(prefix, "", 1)
        return Path(raw_path).resolve()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS page_state (
                    url TEXT PRIMARY KEY,
                    scope TEXT NOT NULL,
                    title TEXT,
                    content_hash TEXT NOT NULL,
                    last_crawled_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chunk_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    title TEXT,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    metadata_json TEXT,
                    embedding_json TEXT,
                    updated_at TEXT NOT NULL
                )
                """
            )
            columns = conn.execute("PRAGMA table_info(chunk_embeddings)").fetchall()
            column_names = {row[1] for row in columns}
            if "metadata_json" not in column_names:
                conn.execute("ALTER TABLE chunk_embeddings ADD COLUMN metadata_json TEXT")

            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_scope ON chunk_embeddings(scope)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_url ON chunk_embeddings(url)")

    def sync_pages(self, pages: list[CrawledPage]) -> dict[str, int]:
        stats = {
            "total_pages": len(pages),
            "changed_pages": 0,
            "unchanged_pages": 0,
            "embedded_chunks": 0,
        }

        with self._connect() as conn:
            for page in pages:
                scope = _scope_from_url(page.url)
                row = conn.execute(
                    "SELECT content_hash FROM page_state WHERE url = ?",
                    (page.url,),
                ).fetchone()

                if row and row["content_hash"] == page.content_hash:
                    stats["unchanged_pages"] += 1
                    continue

                stats["changed_pages"] += 1
                chunks_with_meta = self._prepare_chunks(page)
                chunk_texts = [item["content"] for item in chunks_with_meta]
                embeddings = self._embed_texts(chunk_texts)

                conn.execute("DELETE FROM chunk_embeddings WHERE url = ?", (page.url,))

                now = _utc_now()
                conn.execute(
                    """
                    INSERT INTO page_state(url, scope, title, content_hash, last_crawled_at)
                    VALUES(?, ?, ?, ?, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        scope = excluded.scope,
                        title = excluded.title,
                        content_hash = excluded.content_hash,
                        last_crawled_at = excluded.last_crawled_at
                    """,
                    (page.url, scope, page.title, page.content_hash, now),
                )

                for idx, chunk in enumerate(chunks_with_meta):
                    embedding = embeddings[idx] if embeddings is not None else None
                    conn.execute(
                        """
                        INSERT INTO chunk_embeddings(
                            url, scope, title, chunk_index, content, content_hash, metadata_json, embedding_json, updated_at
                        ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            page.url,
                            scope,
                            page.title,
                            idx,
                            chunk["content"],
                            page.content_hash,
                            json.dumps(chunk["metadata"]),
                            json.dumps(embedding) if embedding else None,
                            now,
                        ),
                    )

                stats["embedded_chunks"] += len(chunks_with_meta)

        return stats

    def retrieve(self, question: str, website_url: str, top_k: int) -> list[RetrievedChunk]:
        scope = _scope_from_url(website_url)
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, url, title, chunk_index, content, metadata_json, embedding_json FROM chunk_embeddings WHERE scope = ?",
                (scope,),
            ).fetchall()

        if not rows:
            return []

        query_embedding = self._embed_single(question)
        weighted: list[dict] = []

        for row in rows:
            content = row["content"]
            semantic_score = 0.0
            if query_embedding is not None and row["embedding_json"]:
                vector = json.loads(row["embedding_json"])
                semantic_score = self._cosine_similarity(query_embedding, vector)

            lexical_score = self._lexical_score(question, content)
            hybrid_score = self._hybrid_score(semantic_score, lexical_score)
            weighted.append(
                {
                    "row": row,
                    "semantic_score": semantic_score,
                    "lexical_score": lexical_score,
                    "hybrid_score": hybrid_score,
                }
            )

        weighted.sort(key=lambda item: item["hybrid_score"], reverse=True)
        pool_size = max(top_k, self.settings.retrieval_rerank_pool)
        pool = weighted[:pool_size]

        reranked = self._rerank(question, pool)
        reranked.sort(key=lambda item: item["rerank_score"], reverse=True)

        scored: list[RetrievedChunk] = []
        for item in reranked[:top_k]:
            row = item["row"]
            content = row["content"]
            snippet = content[:280]
            metadata = self._parse_metadata(row["metadata_json"])

            scored.append(
                RetrievedChunk(
                    citation_id=f"CIT-{row['id']}",
                    url=row["url"],
                    title=row["title"],
                    snippet=snippet,
                    content=content,
                    score=item["rerank_score"],
                    semantic_score=item["semantic_score"],
                    lexical_score=item["lexical_score"],
                    rerank_score=item["rerank_score"],
                    metadata=metadata,
                )
            )
        return scored[:top_k]

    def _embed_texts(self, texts: list[str]) -> list[list[float]] | None:
        if not texts:
            return []
        try:
            return self._embeddings.embed_documents(texts)
        except Exception:
            return None

    def _embed_single(self, text: str) -> list[float] | None:
        try:
            return self._embeddings.embed_query(text)
        except Exception:
            return None

    def _chunk_text(self, text: str) -> list[str]:
        text = " ".join(text.split())
        if not text:
            return []

        chunk_size = self.settings.embedding_chunk_size
        overlap = self.settings.embedding_chunk_overlap
        step = max(1, chunk_size - overlap)

        chunks: list[str] = []
        for start in range(0, len(text), step):
            chunk = text[start : start + chunk_size]
            if chunk:
                chunks.append(chunk)
            if start + chunk_size >= len(text):
                break

        return chunks

    def _prepare_chunks(self, page: CrawledPage) -> list[dict[str, str | int]]:
        if page.structured_segments:
            chunks: list[dict[str, str | int]] = []
            for segment in page.structured_segments:
                cleaned = " ".join(segment.text.split())
                if not cleaned:
                    continue

                if len(cleaned) <= self.settings.embedding_chunk_size:
                    chunks.append(
                        {
                            "content": cleaned,
                            "metadata": {
                                "block_type": segment.block_type,
                                "heading_path": segment.heading_path or "",
                                "source_order": segment.source_order,
                                "source_url": page.url,
                            },
                        }
                    )
                    continue

                chunks.extend(self._split_segment(cleaned, segment, page.url))

            return chunks

        return [
            {
                "content": chunk,
                "metadata": {
                    "block_type": "fallback",
                    "heading_path": "",
                    "source_order": idx,
                    "source_url": page.url,
                },
            }
            for idx, chunk in enumerate(self._chunk_text(page.text))
        ]

    def _split_segment(
        self,
        text: str,
        segment: StructuredSegment,
        source_url: str,
    ) -> list[dict[str, str | int]]:
        chunk_size = self.settings.embedding_chunk_size
        overlap = self.settings.embedding_chunk_overlap
        step = max(1, chunk_size - overlap)

        parts: list[dict[str, str | int]] = []
        part_index = 0
        for start in range(0, len(text), step):
            part = text[start : start + chunk_size]
            if not part:
                continue

            parts.append(
                {
                    "content": part,
                    "metadata": {
                        "block_type": segment.block_type,
                        "heading_path": segment.heading_path or "",
                        "source_order": segment.source_order,
                        "part_index": part_index,
                        "source_url": source_url,
                    },
                }
            )
            part_index += 1

            if start + chunk_size >= len(text):
                break

        return parts

    def _hybrid_score(self, semantic_score: float, lexical_score: float) -> float:
        alpha = min(1.0, max(0.0, self.settings.hybrid_alpha))
        semantic_norm = (semantic_score + 1.0) / 2.0
        lexical_norm = min(1.0, max(0.0, lexical_score))
        return alpha * semantic_norm + (1.0 - alpha) * lexical_norm

    def _rerank(self, query: str, weighted_rows: list[dict]) -> list[dict]:
        query_tokens = [token for token in query.lower().split() if len(token) > 2]
        query_text = " ".join(query_tokens)

        reranked: list[dict] = []
        for item in weighted_rows:
            row = item["row"]
            text = row["content"].lower()
            metadata = self._parse_metadata(row["metadata_json"])

            coverage = 0.0
            if query_tokens:
                matched = sum(1 for token in query_tokens if token in text)
                coverage = matched / len(query_tokens)

            phrase_bonus = 0.1 if query_text and query_text in text else 0.0
            heading_bonus = 0.05 if metadata.get("heading_path") else 0.0

            rerank_score = item["hybrid_score"] * 0.75 + coverage * 0.2 + phrase_bonus + heading_bonus
            reranked.append({**item, "rerank_score": rerank_score})

        return reranked

    def _parse_metadata(self, metadata_json: str | None) -> dict[str, str | int]:
        if not metadata_json:
            return {}
        try:
            parsed = json.loads(metadata_json)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {}
        return {}

    def _lexical_score(self, query: str, text: str) -> float:
        query_tokens = {token for token in query.lower().split() if len(token) > 2}
        if not query_tokens:
            return 0.0

        text_tokens = set(text.lower().split())
        overlap = len(query_tokens.intersection(text_tokens))
        return overlap / len(query_tokens)

    def _cosine_similarity(self, v1: Iterable[float], v2: Iterable[float]) -> float:
        v1_list = list(v1)
        v2_list = list(v2)

        if len(v1_list) != len(v2_list) or not v1_list:
            return 0.0

        dot = sum(a * b for a, b in zip(v1_list, v2_list))
        mag1 = math.sqrt(sum(a * a for a in v1_list))
        mag2 = math.sqrt(sum(b * b for b in v2_list))

        if mag1 == 0.0 or mag2 == 0.0:
            return 0.0

        return dot / (mag1 * mag2)


incremental_index = IncrementalEmbeddingIndex()
