from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from app.core.settings import get_settings


@dataclass
class CrawledPage:
    url: str
    title: str | None
    text: str


class WebsiteCrawler:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def crawl(self, url: str) -> list[CrawledPage]:
        headers = {"User-Agent": self.settings.crawler_user_agent}
        timeout = self.settings.crawler_timeout_seconds

        async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        text = " ".join(soup.get_text(" ", strip=True).split())

        if len(text) > 5000:
            text = text[:5000]

        return [CrawledPage(url=url, title=title, text=text)]
