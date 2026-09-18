from collections import deque
from dataclasses import dataclass
import hashlib
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag

from app.core.settings import get_settings


@dataclass
class StructuredSegment:
    text: str
    block_type: str
    heading_path: str | None
    source_order: int


@dataclass
class CrawledPage:
    url: str
    title: str | None
    text: str
    content_hash: str
    structured_segments: list[StructuredSegment]


class WebsiteCrawler:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def crawl(self, url: str) -> list[CrawledPage]:
        start_url = self._normalize_url(url)
        start_domain = urlparse(start_url).netloc
        queue: deque[str] = deque([start_url])
        visited: set[str] = set()
        pages: list[CrawledPage] = []

        headers = {"User-Agent": self.settings.crawler_user_agent}
        timeout = self.settings.crawler_timeout_seconds
        max_pages = max(1, self.settings.crawler_max_pages)

        async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
            while queue and len(pages) < max_pages:
                current_url = queue.popleft()
                if current_url in visited:
                    continue

                visited.add(current_url)

                try:
                    response = await client.get(current_url)
                    response.raise_for_status()
                except Exception:
                    continue

                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                title = soup.title.string.strip() if soup.title and soup.title.string else None
                segments = self._extract_structured_segments(soup)
                text = "\n\n".join(segment.text for segment in segments)

                if len(text) > 20000:
                    text = text[:20000]
                    segments = self._split_text_for_hash(text)

                pages.append(
                    CrawledPage(
                        url=current_url,
                        title=title,
                        text=text,
                        content_hash=self._hash_content(text),
                        structured_segments=segments,
                    )
                )

                for discovered_url in self._extract_links(soup, current_url, start_domain):
                    if discovered_url not in visited and discovered_url not in queue:
                        queue.append(discovered_url)

        return pages

    def _extract_links(self, soup: BeautifulSoup, base_url: str, allowed_domain: str) -> list[str]:
        links: list[str] = []
        for anchor in soup.find_all("a", href=True):
            candidate = self._normalize_url(urljoin(base_url, anchor["href"]))
            parsed = urlparse(candidate)
            if parsed.netloc != allowed_domain:
                continue
            if parsed.scheme not in {"http", "https"}:
                continue
            links.append(candidate)
        return links

    def _normalize_url(self, url: str) -> str:
        cleaned, _ = urldefrag(url)
        return cleaned.rstrip("/")

    def _hash_content(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _extract_structured_segments(self, soup: BeautifulSoup) -> list[StructuredSegment]:
        self._remove_boilerplate(soup)
        root = self._pick_main_content_root(soup)
        if root is None:
            return []

        segments: list[StructuredSegment] = []
        heading_stack: dict[int, str] = {}
        target_tags = {"h1", "h2", "h3", "h4", "p", "li", "th", "td", "pre", "blockquote"}
        source_order = 0

        for node in root.find_all(target_tags):
            if not isinstance(node, Tag):
                continue

            text = " ".join(node.get_text(" ", strip=True).split())
            if not text:
                continue

            if node.name in {"h1", "h2", "h3", "h4"}:
                level = int(node.name[1])
                heading_stack[level] = text
                for depth in list(heading_stack.keys()):
                    if depth > level:
                        del heading_stack[depth]
                continue

            if len(text) < 35 and node.name not in {"li", "th", "td"}:
                continue

            heading_path = " > ".join(heading_stack[idx] for idx in sorted(heading_stack.keys()))
            segment = StructuredSegment(
                text=text,
                block_type=node.name,
                heading_path=heading_path if heading_path else None,
                source_order=source_order,
            )

            if not segments or segments[-1].text != segment.text:
                segments.append(segment)
                source_order += 1

        if not segments:
            fallback = " ".join(root.get_text(" ", strip=True).split())
            if fallback:
                segments = self._split_text_for_hash(fallback)

        return segments

    def _remove_boilerplate(self, soup: BeautifulSoup) -> None:
        boilerplate_selectors = [
            "script",
            "style",
            "noscript",
            "svg",
            "canvas",
            "iframe",
            "nav",
            "footer",
            "header",
            "aside",
            "form",
        ]
        for selector in boilerplate_selectors:
            for node in soup.select(selector):
                node.decompose()

    def _pick_main_content_root(self, soup: BeautifulSoup) -> Tag | None:
        main_node = soup.find("main")
        if isinstance(main_node, Tag):
            return main_node

        article_node = soup.find("article")
        if isinstance(article_node, Tag):
            return article_node

        role_main = soup.find(attrs={"role": "main"})
        if isinstance(role_main, Tag):
            return role_main

        if isinstance(soup.body, Tag):
            return soup.body

        return None

    def _split_text_for_hash(self, text: str) -> list[StructuredSegment]:
        window = 1200
        cleaned = " ".join(text.split())
        chunks: list[StructuredSegment] = []
        source_order = 0
        for idx in range(0, len(cleaned), window):
            part = cleaned[idx : idx + window]
            if not part:
                continue
            chunks.append(
                StructuredSegment(
                    text=part,
                    block_type="fallback",
                    heading_path=None,
                    source_order=source_order,
                )
            )
            source_order += 1

        return chunks
