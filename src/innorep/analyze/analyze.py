import asyncio
from enum import Enum
from typing import Type

from pydantic import BaseModel
from openai import AsyncOpenAI
from innorep.llm.utils import batch_process_openai


class Sentiment(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"


class Spam(str, Enum):
    spam = "spam"
    not_spam = "not_spam"


class CommentAnalysis(BaseModel):
    sentiment: Sentiment
    spam: Spam


SENTIMENT_SPAM_INSTRUCTION = (
    "Analyze the Instagram post comment, determine the sentiment, and classify whether it is spam."
)


async def classify_comment(
    instruction,
    comment: str = "",
    response_format: Type[BaseModel] = CommentAnalysis,
    model: str = "gpt-4o-mini"
):
    client = AsyncOpenAI()
    messages=[{"role": "system", "content": instruction}, {"role": "user", "content": f" Comment: {comment}"}]
    completion = await client.beta.chat.completions.parse(
        model=model, messages=messages, response_format=response_format)
    message = completion.choices[0].message
    if message.parsed:
        return message.parsed
    else:
        print(message.refusal)
        raise ValueError("OpenAI model failed to parse output")


async def analyze_comments(comments: list[dict], batch_size: int = 30) -> list[dict]:
    """Analyzes a list of comments for sentiment and spam using the batch_process function."""

    async def process_batch(batch: list[dict]) -> list[dict]:
        """Processes a single batch of comments."""
        batch_prompts = [comment['text'] for comment in batch]
        tasks = [classify_comment(SENTIMENT_SPAM_INSTRUCTION, comment) for comment in batch_prompts]
        batch_results = await asyncio.gather(*tasks)


        return [
            {
                'id': batch[j]['id'],
                'created_at': batch[j]['created_at'],
                'comment': batch[j]['text'],
                'sentiment': batch_results[j].sentiment,
                'spam': batch_results[j].spam,
            }
            for j in range(len(batch))
        ]

    return await batch_process_openai(comments, batch_size=batch_size, process_batch=process_batch)


def calculate_metrics(sentiment_results):
    """Calculates metrics based on sentiment analysis results."""

    total_comments = len(sentiment_results)
    total_spam = sum(1 for result in sentiment_results if result['spam'] == "spam")
    total_comment_length = sum(len(c['comment']) for c in sentiment_results)

    # # NPS Calculation Logic
    # promoters = sum(1 for result in sentiment_results if result['sentiment_score'] >= 9)
    # detractors = sum(1 for result in sentiment_results if result['sentiment_score'] <= 6)
    # passives = sum(1 for result in sentiment_results if 7 <= result['sentiment_score'] <= 8)
    #
    # valid_responses = promoters + detractors + passives
    #
    # if valid_responses > 0:
    #     nps_score = ((promoters - detractors) / valid_responses) * 100
    # else:
    #     nps_score = 0

    # Calculate the metrics
    metrics = {
        "total_comments": total_comments,
        "average_comment_length": total_comment_length / total_comments if total_comments > 0 else 0,
        "spam_rate": total_spam / total_comments if total_comments > 0 else 0,
        # "nps_score": nps_score,
    }

    return metrics
