import asyncio
import sys
if sys.platform=='win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import nest_asyncio
nest_asyncio.apply()
import random
from crawl4ai import *



async def crawler_main1(url):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url=url,
        )
        return(result.markdown)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0",
]

headers = {
    "User-Agent": random.choice(USER_AGENTS),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

base_browser = BrowserConfig(
    headers=headers,
    headless=True,
    text_mode=True)

async def crawler_main(url):
    async with AsyncWebCrawler(
        config=base_browser,
        headless=True,  # Keep headless mode
        use_stealth=True  # Mimic human browsing behavior
    ) as crawler:
        result = await crawler.arun(
            url=url,
            wait_until="networkidle",
            timeout=90000,  # Increase timeout in case of slow loading
        )
        return result.markdown

