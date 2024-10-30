from pathlib import Path
import json
from datetime import datetime
from src.innorep.scrape import instagram

output = Path(__file__).parent / "scrape_results"
output.mkdir(exist_ok=True)


async def scrape(username: str, posts_max_pages: int = 3):
    # enable scrapfly cache?
    instagram.BASE_CONFIG["cache"] = True
    instagram.BASE_CONFIG["debug"] = True

    print("running Instagram scrape and saving results to ./scrape_results directory")
    timestamp = datetime.now().isoformat()

    user_info = await instagram.scrape_user(username)
    output.joinpath(f"user_{username}.json").write_text(
        json.dumps(
            {
                "user_info": user_info,
                "username": username,
                "timestamp": timestamp,
            },
            indent=2,
            ensure_ascii=False
        ),
        encoding='utf-8'
    )
    user_id = user_info['id']

    posts_all = []
    async for post in instagram.scrape_user_posts(user_id, max_pages=posts_max_pages):
        posts_all.append(post)
    output.joinpath(f"all-user-posts_{username}.json").write_text(
        json.dumps(
            {
                "posts_all": posts_all,
                "username": username,
                "timestamp": timestamp,

            },
            indent=2,
            ensure_ascii=False
        ),
        encoding='utf-8'
    )
