import ast
import logging
from typing import Type

from dspy import ChainOfThought, Assert, Signature, InputField, OutputField

from dslmodel.utils.dspy_tools import init_instant

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


# Helper function to evaluate dictionary from string
def eval_output_str(output_str: str):
    """Safely convert str to Python primitive."""
    try:
        return ast.literal_eval(output_str.strip())
    except (SyntaxError, ValueError, TypeError) as e:
        logger.error(f"Evaluation error: {e}")
        return None


# ===========================
# Define Signature Classes for Each Primitive Type
# ===========================

class PromptToIntSignature(Signature):
    """Synthesize the prompt into an integer."""

    prompt = InputField(desc="The prompt that describes the value to be converted into an integer.")
    output = OutputField(prefix="```python\ninteger_output: int = ",
                                 desc="The integer generated from the prompt.")


class PromptToFloatSignature(Signature):
    """Synthesize the prompt into a float."""

    prompt = InputField(desc="The prompt that describes the value to be converted into a float.")
    output = OutputField(prefix="```python\nfloat_output: float = ",
                               desc="The float value generated from the prompt.")


class PromptToStrSignature(Signature):
    """Synthesize the prompt into a string."""

    prompt = InputField(desc="The prompt that describes the value to be converted into a string.")
    output = OutputField(prefix="```python\nstring_output: str = ", desc="The string generated from the prompt.")


class PromptToBoolSignature(Signature):
    """Synthesize the prompt into a boolean."""

    prompt = InputField(desc="The prompt that describes the value to be converted into a boolean.")
    output = OutputField(prefix="```python\nbool_output: bool = ",
                              desc="The boolean value generated from the prompt.")


class PromptToListSignature(Signature):
    """
    Synthesize the prompt into a list.

    Example:
    prompt: "Generate a list of 3 random numbers."
    output: "```python\nlist_output: list = [1, 2, 3]\n```"

    Example:
    prompt: "Generate a list of 5 random strings."
    output: "```python\nlist_output: list = ['hello', 'world', 'this', 'is', 'python']\n```"

    YOU CAN ONLY RETURN list_output. YOU WILL BE PENALIZED FOR ANY OTHER OUTPUT
    """

    prompt = InputField(desc="The prompt that describes the list to be generated.")
    example = OutputField(desc="An example of the list to be generated.")
    output = OutputField(prefix="```python\nlist_output: list = ", desc="The list generated from the prompt.")


class PromptToDictSignature(Signature):
    """Synthesize the prompt into a dictionary."""

    prompt = InputField(desc="The prompt that describes the dictionary to be generated.")
    output = OutputField(prefix="```python\ndict_output: dict = ",
                              desc="The dictionary generated from the prompt.")


# ===========================
# Error Handling Signatures (Optional, as needed)
# ===========================

class PromptToIntErrorSignature(Signature):
    """Handle errors when synthesizing the prompt into an integer."""

    error_message = InputField(desc="The error message indicating why the integer creation failed.")
    generated_output = InputField(desc="The output that was generated but failed to meet the integer format.")
    prompt = InputField(desc="The prompt that was used to generate the integer.")
    how_to_fix = OutputField(prefix="```python\nfix_suggestion: str = ", desc="A suggestion for how to fix the prompt.")
    output = OutputField(prefix="```python\ncorrected_integer_output: int = ",
                                           desc="The corrected integer output.")


class PromptToFloatErrorSignature(Signature):
    """Handle errors when synthesizing the prompt into a float."""

    error_message = InputField(desc="The error message indicating why the float creation failed.")
    generated_output = InputField(desc="The output that was generated but failed to meet the float format.")
    prompt = InputField(desc="The prompt that was used to generate the float.")
    how_to_fix = OutputField(prefix="```python\nfix_suggestion: str = ", desc="A suggestion for how to fix the prompt.")
    output = OutputField(prefix="```python\ncorrected_float_output: float = ",
                                         desc="The corrected float output.")


# ===========================
# Generic Primitive Module for Generation & Validation
# ===========================

class GenPrimitiveModule:
    """A generic module for generating and validating primitive types from prompts."""

    def __init__(self, primitive_type, generate_sig: Type[Signature], error_sig: Type[Signature], verbose=False):
        """
        Initialize the module with the expected primitive type and the relevant DSPy signatures.

        Args:
        - primitive_type: The expected Python primitive type (e.g., int, float, str, etc.).
        - generate_sig: The DSPy signature class for generating the primitive.
        - error_sig: The DSPy signature class for handling errors during generation.
        - verbose: Whether to enable verbose logging.
        """
        self.primitive_type = primitive_type
        self.generate_sig = generate_sig
        self.error_sig = error_sig
        self.verbose = verbose
        self.output_key = "output"

        # Initialize DSPy ChainOfThought modules for generation and error correction
        self.generate = ChainOfThought(generate_sig)
        self.correct_generate = ChainOfThought(error_sig)
        self.validation_error = None

    def eval_output(self, output: str):
        """
        Attempt to evaluate the generated output string into the correct Python primitive type.
        """
        return eval_output_str(output)

    def validate_output(self, output) -> bool:
        """
        Validates whether the output matches the expected primitive type.
        """
        is_valid = isinstance(output, self.primitive_type)
        Assert(is_valid, f"Expected {self.primitive_type.__name__}, but got {type(output).__name__}.")
        return is_valid

    def forward(self, prompt: str):
        """
        Handles generation, validation, correction, and returns the final output.
        """
        # Generate initial output
        generated_output = self.generate(prompt=prompt)
        output = generated_output.get(self.output_key)

        # Attempt to evaluate the output to the expected primitive type
        evaluated_output = self.eval_output(output)

        # Validate the output
        try:
            if self.validate_output(evaluated_output):
                return evaluated_output
        except AssertionError as e:
            logger.warning(f"Validation failed: {e}. Trying correction...")

        # Attempt to correct the output
        corrected_output = self.correct_generate(prompt=prompt, error="Validation failed", generated_output=output)
        corrected_evaluated_output = self.eval_output(corrected_output.get(self.output_key))

        # Validate corrected output
        Assert(self.validate_output(corrected_evaluated_output),
               f"Correction failed to generate valid {self.primitive_type.__name__}.")
        return corrected_evaluated_output

    def __call__(self, prompt: str):
        return self.forward(prompt)


# ===========================
# Submodules for Each Primitive Type
# ===========================

class GenIntModule(GenPrimitiveModule):
    """Module for generating and validating integer values."""

    def __init__(self, verbose=False):
        super().__init__(
            primitive_type=int,
            generate_sig=PromptToIntSignature,
            error_sig=PromptToIntErrorSignature,
            verbose=verbose
        )


class GenFloatModule(GenPrimitiveModule):
    """Module for generating and validating float values."""

    def __init__(self, verbose=False):
        super().__init__(
            primitive_type=float,
            generate_sig=PromptToFloatSignature,
            error_sig=PromptToFloatErrorSignature,
            verbose=verbose
        )


class GenStrModule(GenPrimitiveModule):
    """Module for generating and validating string values."""

    def __init__(self, verbose=False):
        super().__init__(
            primitive_type=str,
            generate_sig=PromptToStrSignature,
            error_sig=PromptToIntErrorSignature,
            # Assuming this error signature for now, you can add PromptToStrErrorSignature if needed.
            verbose=verbose
        )


class GenBoolModule(GenPrimitiveModule):
    """Module for generating and validating boolean values."""

    def __init__(self, verbose=False):
        super().__init__(
            primitive_type=bool,
            generate_sig=PromptToBoolSignature,
            error_sig=PromptToIntErrorSignature,
            # Assuming same error sig, you can extend to PromptToBoolErrorSignature.
            verbose=verbose
        )


class GenListModule(GenPrimitiveModule):
    """Module for generating and validating list values."""

    def __init__(self, verbose=False):
        super().__init__(
            primitive_type=list,
            generate_sig=PromptToListSignature,
            error_sig=PromptToIntErrorSignature,  # Extend to PromptToListErrorSignature if needed.
            verbose=verbose
        )

    def eval_output(self, output: str):
        """
        Attempt to evaluate the generated output string into the correct Python primitive type.
        """
        list_part = output.split("list = ", 1)[1].strip("```").strip()
        return eval_output_str(list_part)


class GenDictModule(GenPrimitiveModule):
    """Module for generating and validating dictionary values."""

    def __init__(self, verbose=False):
        super().__init__(
            primitive_type=dict,
            generate_sig=PromptToDictSignature,
            error_sig=PromptToIntErrorSignature,  # Extend to PromptToDictErrorSignature if needed.
            verbose=verbose
        )


# ===========================
# Generation Functions (gen_{type})
# ===========================

def gen_int(prompt: str):
    return GenIntModule()(prompt)


def gen_float(prompt: str):
    return GenFloatModule()(prompt)


def gen_str(prompt: str):
    return GenStrModule()(prompt)


def gen_bool(prompt: str):
    return GenBoolModule()(prompt)


def gen_list(prompt: str) -> list:
    return GenListModule()(prompt)


def gen_dict(prompt: str):
    return GenDictModule()(prompt)


# Example Usage:

if __name__ == "__main__":
    init_instant()
    # Example: Generate an integer
    prompt = "How many planets are in the solar system?"
    result = gen_int(prompt)
    print(f"Generated Integer: {result}")

    # Example: Generate a list
    prompt = "List the planets in the solar system."
    result = gen_list(prompt)
    print(f"Generated List: {result}")
