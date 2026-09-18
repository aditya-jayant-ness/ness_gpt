from app.graph.state import ChatGraphState
from app.services.crawler.service import WebsiteCrawler

crawler = WebsiteCrawler()


async def crawl_website(state: ChatGraphState) -> ChatGraphState:
    pages = await crawler.crawl(state["website_url"])
    chunks = [page.text for page in pages]
    sources = [{"url": page.url, "title": page.title or "Untitled", "snippet": page.text[:280]} for page in pages]
    state["crawled_chunks"] = chunks
    state["sources"] = sources
    return state
