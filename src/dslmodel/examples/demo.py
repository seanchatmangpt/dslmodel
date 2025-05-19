import dspy
import asyncio
from typing import Dict, Any, Tuple

async def analyze_topic_async(topic: str) -> Dict[str, Any]:
    """Analyze a topic across multiple categories using DSPy.
    
    Args:
        topic: The topic to analyze
        
    Returns:
        A dictionary mapping categories to their analyses
    """
    # Define the categories and their corresponding output fields
    analyses = dict(
        tech="overview, state_of_the_art, future_directions",
        business="market_analysis, competition, strategy",
        marketing="target_audience, channels, campaigns",
        finance="budgeting, forecasting, investments",
        competitive_intelligence="competitors, market_share, trends"
    )

    # Worker function to process a single category asynchronously
    async def analyze_category(category: str, outputs: str) -> Tuple[str, Any]:
        try:
            chain = dspy.ChainOfThought(f"topic -> {outputs}")
            result = chain(topic=topic)
            return category, result
        except Exception as e:
            return category, f"Error: {str(e)}"

    # Run all analyses concurrently using asyncio.gather
    results = await asyncio.gather(
        *(analyze_category(category, outputs) for category, outputs in analyses.items())
    )

    # Convert results to dictionary
    return dict(results)

async def main():
    """Run the demo analysis."""
    results = await analyze_topic_async("Microsoft Copilots")
    for category, analysis in results.items():
        print(f"Category: {category}")
        print(f"Analysis: {analysis}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())

