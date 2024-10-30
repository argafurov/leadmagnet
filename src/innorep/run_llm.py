import json
import asyncio
from pathlib import Path
from datetime import datetime

from src.innorep.analyze.analyze import analyze_comments, calculate_metrics


input_dir = Path(__file__).parent / "scrape_results"
output_dir = Path(__file__).parent / "analysis_results"
output_dir.mkdir(exist_ok=True)


def get_latest_file(username: str, prefix: str) -> Path:
    """Finds the latest JSON file for the user with the given prefix."""
    files = list(input_dir.glob(f"{prefix}_{username}.json"))
    if not files:
        raise FileNotFoundError(f"No files found for user {username} with prefix {prefix}")
    return max(files, key=lambda f: f.stat().st_mtime)


def main(username: str, batch_size: int = 30):
    # Load user data (as before)
    user_file = get_latest_file(username, "user")
    with open(user_file, 'r', encoding='utf-8') as f:
        user_data = json.load(f)

    # Load posts data (as before)
    posts_file = get_latest_file(username, "all-user-posts")
    with open(posts_file, 'r', encoding='utf-8') as f:
        posts_data = json.load(f)

    comments = []
    for post in posts_data['posts_all']:
        comments.extend(post.get('comments', []))

    # Analyze comments asynchronously
    results = asyncio.run(analyze_comments(comments, batch_size=batch_size))

    # Calculate metrics
    metrics = calculate_metrics(results)

    # Prepare analysis data
    analysis = {
        "username": username,
        "metrics": metrics,
        "llm_results": results,
        "timestamp": datetime.now().isoformat()
    }

    # Save analysis data to JSON
    output_dir.joinpath(f"analysis_{username}.json").write_text(
        json.dumps(analysis, indent=2, ensure_ascii=False), encoding='utf-8')
