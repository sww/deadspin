import asyncio
import logging
import json
import urllib.parse

import aiohttp


logging.basicConfig(
    level=logging.DEBUG, format="[%(levelname)-4s] %(name)s:%(asctime)-15s %(message)s"
)

BASE_URL = f"https://deadspin.com/ajax/comments/views/replies/"


async def get_comments(post_id):
    comments = []

    async with aiohttp.ClientSession() as session:
        base_url = f"{BASE_URL}{post_id}"
        params = {"cache": "true", "sorting": "top"}

        while True:
            url = f"{base_url}?{urllib.parse.urlencode(params)}"

            async with session.get(url) as response:
                logging.info("Getting comments from url: %s", url)

                if response.status != 200:
                    logging.error(
                        "Got a non-200 response code: %s, breaking...", response.status
                    )
                    break

                content = await response.read()
                body = json.loads(content)

                meta_error = body.get("meta", {}).get("error")
                if meta_error:
                    logging.error("Got an error: %s", meta_error)
                    return

                data = body.get("data")

                items = data.get("items")
                logging.debug("Got %s comments", len(items))
                comments.extend(items)

                pagination = data.get("pagination")
                if not pagination:
                    logging.debug("No pagination, breaking...")
                    break

                if not pagination.get("next"):
                    logging.debug("All comments retrieved, breaking...")
                    break

                current_page = pagination.get("curr")
                next_page = pagination.get("next")

                start_index = next_page.get("startIndex")

                if start_index >= next_page.get("total"):
                    logging.debug("All paginated comments retrieved, breaking...")
                    break

                params["startIndex"] = start_index

                asyncio.sleep(1.5)

    return comments


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    post_id = 1839471181

    with open(f"{post_id}.json", "w") as f:
        c = loop.run_until_complete(get_comments(post_id))
        json.dump(c, f)
