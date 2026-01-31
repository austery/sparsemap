import hashlib
from typing import Tuple

import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException

from sparsemap.core.config import get_settings


def hash_url(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


async def fetch_url_content(url: str) -> Tuple[str, str]:
    settings = get_settings()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
    }
    try:
        async with httpx.AsyncClient(
            timeout=15.0, headers=headers, follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 403:
            raise HTTPException(
                status_code=400,
                detail="无法访问该 URL（403 Forbidden）。建议复制页面内容直接粘贴。",
            ) from exc
        raise HTTPException(
            status_code=400,
            detail=f"无法抓取 URL 内容: HTTP {exc.response.status_code}",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=400, detail=f"无法抓取 URL 内容: {exc}"
        ) from exc

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()

    main_content = (
        soup.find("main") or soup.find("article") or soup.find("div", class_="content")
    )
    if main_content:
        text = main_content.get_text(separator="\n", strip=True)
    else:
        body = soup.find("body")
        if body:
            text = body.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    cleaned = "\n".join(lines)

    if len(cleaned) < settings.extractor_min_chars:
        raise HTTPException(
            status_code=400, detail="抓取内容过短，请提供更完整的内容。"
        )

    return cleaned[: settings.extractor_max_chars], hash_url(url)
