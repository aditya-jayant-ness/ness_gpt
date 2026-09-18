import asyncio

from app.core.settings import get_settings
from app.graph.state import ChatGraphState
from app.services.crawler.service import WebsiteCrawler
from app.services.retrieval.incremental_index import incremental_index

crawler = WebsiteCrawler()
settings = get_settings()


async def crawl_website(state: ChatGraphState) -> ChatGraphState:
    pages = await crawler.crawl(state["website_url"])
    sync_stats = await asyncio.to_thread(incremental_index.sync_pages, pages)
    retrieved = await asyncio.to_thread(
        incremental_index.retrieve,
        state["question"],
        state["website_url"],
        settings.retrieval_top_k,
    )

    state["crawled_chunks"] = [item.content for item in retrieved]
    state["sources"] = [
        {
            "citation_id": item.citation_id,
            "url": item.url,
            "title": item.title or "Untitled",
            "snippet": item.snippet,
            "score": round(item.rerank_score, 4),
            "metadata": {
                **item.metadata,
                "semantic_score": round(item.semantic_score, 4),
                "lexical_score": round(item.lexical_score, 4),
                "hybrid_rerank_score": round(item.rerank_score, 4),
            },
        }
        for item in retrieved
    ]
    state["crawl_stats"] = sync_stats
    state["tool_events"].append({"type": "crawl_sync", "stats": sync_stats})
    return state
