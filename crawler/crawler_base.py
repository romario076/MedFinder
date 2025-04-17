import asyncio
import sys
if sys.platform=='win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import nest_asyncio
nest_asyncio.apply()
import random
import requests
from bs4 import BeautifulSoup


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

async def crawler_main(url):
    print('[INFO] Base crawler get: '+ url)
    try:
        # Define headers to mimic a browser request
        headers = {
            "User-Agent": random.choice(USER_AGENTS)
        }

        # Fetch the webpage content
        response = requests.get(url, headers=headers)

        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract all text and remove extra whitespace
        text_content = soup.get_text(separator="\n")
        cleaned_text = "\n".join(line.strip() for line in text_content.splitlines() if line.strip())

        # Format as Markdown
        markdown_content = f"# {url}\n\n" + cleaned_text
    except Exception as e:
        print('[ERROR] Base crawler Error: '  +str(e))
    else:
        print('[SUCCESS] Base Crawler: ' + str(url))
    return markdown_content