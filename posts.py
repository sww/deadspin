import asyncio
import logging
import urllib.parse

import aiohttp
from bs4 import BeautifulSoup


logging.basicConfig(
    level=logging.DEBUG, format="[%(levelname)-4s] %(name)s:%(asctime)-15s %(message)s"
)

BASE_URL = "https://www.deadspin.com"


async def get_post_ids(start_time=0, pages=10):
    post_ids = []
    pages_seen = 0

    async with aiohttp.ClientSession() as session:
        params = {}
        if start_time:
            params = {"startTime": start_time}

        while pages_seen < pages:
            url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"

            async with session.get(url) as response:
                if response.status != 200:
                    logging.error(
                        "Got non-200 response code: %s, returning...", response.status
                    )
                    return post_ids

                data = await response.read()

                soup = BeautifulSoup(data, "html.parser")
                for article in soup.find_all("article"):
                    if "data-id" not in article.attrs:
                        continue

                    post_ids.append(article.attrs["data-id"])

                more_stories = soup.select_one('a[href*="?startTime"]')
                if not more_stories:
                    logging.info(
                        'Could not find the "More Stories" button, breaking...'
                    )
                    break

                params["startTime"] = more_stories.attr("href").split("=")[-1]

                asyncio.sleep(1.5)

            pages_seen += 1

    return post_ids


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_post_ids)
