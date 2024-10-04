from typing import Type, TypeVar, Union
import dspy

T = TypeVar("T", bound="DSLModel")


class DSPyDSLMixin:
    """
    A mixin class that provides functionality to create a model instance from a DSPy signature
    (string or dspy.Signature) and a predictor class. The default predictor class is dspy.Predict.
    """

    @classmethod
    def from_prompt(cls: Type[T], prompt: str, verbose=False, **kwargs) -> T:
        """
        Creates an instance of the model from a user prompt.

        :param prompt: The user prompt.
        :param verbose: Whether to print verbose output and debug information.
        :return: An instance of the model.
        """
        from dslmodel.template import render
        from dslmodel.dspy_modules.gen_pydantic_instance import gen_instance

        prompt = render(prompt, **kwargs)

        if verbose:
            print(f"Prompt: {prompt}")

        return gen_instance(cls, prompt, verbose)

    @classmethod
    def from_signature(
            cls: Type[T],
            signature: Union[str, Type[dspy.Signature]],  # Signature can be a string or a dspy.Signature subclass
            predictor_class: Type[dspy.Module] = dspy.Predict,  # Default predictor class is dspy.Predict
            verbose=False,
            **kwargs
    ) -> T:
        """
        Creates an instance of the model using a DSPy signature (either a string or a dspy.Signature)
        and a predictor class. If no predictor class is provided, dspy.Predict is used by default.

        :param signature: The DSPy signature, defining input/output behavior (e.g., "sentence -> sentiment"),
                          or a signature class (dspy.Signature).
        :param predictor_class: A DSPy module class (dspy.Module) that can interpret the signature and generate a prompt.
                                Default is dspy.Predict.
        :param verbose: Whether to print verbose output and debug information.
        :return: An instance of the model.
        """
        # Instantiate the predictor with the provided signature (string or Signature subclass)
        predictor = predictor_class(signature)

        # Use the predictor to generate a prompt based on the signature
        prompt = predictor(**kwargs)

        if verbose:
            print(f"Prompt: {prompt}")

        # Create an instance of the model using from_prompt
        return cls.from_prompt(str(prompt), verbose=verbose, **kwargs)
