import dspy
import asyncio

async def analyze_topic_async(topic: str):
    # Define the categories and their corresponding output fields.
    analyses = dict(
        tech="overview, state_of_the_art, future_directions",
        business="market_analysis, competition, strategy",
        marketing="target_audience, channels, campaigns",
        finance="budgeting, forecasting, investments",
        competitive_intelligence="competitors, market_share, trends"
    )

    # Worker function to process a single category asynchronously.
    async def analyze_category(category, outputs):
        chain = dspy.ChainOfThought(f"topic -> {outputs}")
        return category, chain(topic=topic)

    # Run all analyses concurrently using asyncio.gather.
    results = await asyncio.gather(
        *(analyze_category(category, outputs) for category, outputs in analyses.items()),
        return_exceptions=True
    )

    # Process results: handle exceptions gracefully.
    return {category: result if not isinstance(result, Exception) else f"Error: {result}"
            for category, result in results}

# Example usage.
async def main():
    results = await analyze_topic_async("Microsoft Copilots")
    for category, analysis in results.items():
        print(f"Category: {category}")
        print(f"Analysis: {analysis}")
        print("-" * 50)

# Run the async function.
asyncio.run(main())

