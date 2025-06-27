from typing import List

from dslmodel import DSLModel


# Define Pydantic models for structured outputs
class FitnessScore(DSLModel):
    individual: str
    score: str

class SelectionResponse(DSLModel):
    selected: List[str]

class CrossoverResponse(DSLModel):
    child: str

class MutationResponse(DSLModel):
    mutated: str

class FinalSelectionResponse(DSLModel):
    best_individual: str



def llm_genetic(prompt: str, pop_size: int = 10, generations: int = 5) -> str:
    # Create the initial population of strings
    population = [f"Individual {i}" for i in range(1, pop_size + 1)]

    for generation in range(generations):
        print(f"Generation {generation + 1}")

        # Step 1: Fitness Evaluation
        fitness_scores = []
        for individual in population:
            fitness_score = FitnessScore.from_prompt(
                f"Task: {prompt}\nEvaluate this string: {individual}"
            )
            if fitness_score:
                fitness_scores.append((fitness_score.individual, fitness_score.score))

        # Step 2: Selection (LLM decides which individuals to select)
        selected_population = SelectionResponse.from_prompt(
            f"Task: {prompt}\nIndividuals with scores: {fitness_scores}"
        ).selected

        # Step 3: Crossover (LLM combines two individuals)
        new_population = []
        for i in range(0, len(selected_population), 2):
            if i + 1 < len(selected_population):
                parent1 = selected_population[i]
                parent2 = selected_population[i + 1]
                crossover_result = CrossoverResponse.from_prompt(
                    f"Task: {prompt}\nCombine the following strings:\nParent 1: {parent1}\nParent 2: {parent2}"
                )
                if crossover_result:
                    new_population.append(crossover_result.child)

        # Step 4: Mutation (LLM mutates the individuals)
        mutated_population = []
        for individual in new_population:
            mutation_result = MutationResponse.from_prompt(
                f"Task: {prompt}\nMake a small mutation to this string: {individual}"
            )
            if mutation_result:
                mutated_population.append(mutation_result.mutated)

        # Update the population with mutated individuals
        population = mutated_population

        # Print the population for the current generation
        print(f"Population at Generation {generation + 1}: {population}\n")

    # Return the best individual as the final result
    final_selection = FinalSelectionResponse.from_prompt(
        f"Task: {prompt}\nSelect the best string from the final population: {population}"
    )

    best_individual = final_selection.best_individual if final_selection else "No result"
    print(f"Best individual after evolution: {best_individual}")
    return best_individual


def main():
    """Main function"""
    from dslmodel import init_lm, init_instant, init_text
    init_instant()
    # Example usage
    prompt = "Create the most creative story title."
    result = llm_genetic(prompt)
    print("Evolved result:", result)


if __name__ == '__main__':
    main()
