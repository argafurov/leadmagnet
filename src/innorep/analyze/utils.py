from typing import Callable, Any


instruction_extract_base = (
    "You are an expert extraction algorithm. Only extract relevant information from the text. "
    "Avoid inserting double quotes or curly brackets into the output. "
    "If you do not know the value of an attribute asked to extract, return null for the attribute's value."
)


async def batch_process_openai(
    items: list[Any],
    batch_size: int,
    process_batch: Callable[[list[Any]], Any]
) -> list[Any]:
    """
    Processes a list of items in batches of a given size using the specified processing function.

    :param items: The list of items to be processed.
    :param batch_size: The size of each batch.
    :param process_batch: A function that takes a list of items and returns the processed results.

    :return: A list of results after processing all batches.
    """
    total_items = len(items)
    results = []

    print(f"Starting processing of {total_items} items in batches of {batch_size}...")

    for i in range(0, total_items, batch_size):
        batch = items[i:i + batch_size]

        print(f"Processing batch {i // batch_size + 1} with {len(batch)} items...")

        batch_results = await process_batch(batch)
        results.extend(batch_results)

        print(f"Batch {i // batch_size + 1} processed.")

    print("Processing complete.")
    return results
