import typing

import dspy
from pydantic import BaseModel, Field

if typing.TYPE_CHECKING:
    from dspygen.mixin.tool.tool_mixin import ToolMixin


class ChosenTool(BaseModel):
    reasoning: str = Field(..., description="Step-by-step reasoning about which tool to choose.")
    chosen_tool: str = Field(..., description="The chosen tool based on the command.")


class ToolTriggerModule(dspy.Module):
    """ToolTriggerModule selects the best tool for a given prompt."""

    def __init__(self, **forward_args):
        super().__init__()
        self.forward_args = forward_args
        self.output = None

    def forward(self, prompt: str, tool_mixin: "ToolMixin") -> str:
        # Determine the best tool to trigger for the given voice command or prompt
        from dspygen.modules.json_module import json_call

        possible_tools = "\n".join(tool_mixin.possible_tools())

        text = (
            f"```prompt\n{prompt}\n```\n\n"
            f"Choose from Possible Tools based on prompt:\n\n```possible_tools\n{possible_tools}\n```\n\n"
            f"You must choose one of the possible tools to proceed."
        )

        # logger.info(text)

        response = json_call(ChosenTool, text=text)

        return response.chosen_tool


def tool_trigger_call(prompt: str, tool_mixin: "ToolMixin", **kwargs):
    """Triggers the appropriate tool from ToolMixin based on the prompt."""
    tool_trigger = ToolTriggerModule()
    chosen_tool = tool_trigger.forward(prompt=prompt, tool_mixin=tool_mixin)
    if chosen_tool and hasattr(tool_mixin, chosen_tool):
        action = getattr(tool_mixin, chosen_tool)
        action(**kwargs)
    else:
        raise ValueError(f"No valid tool for command '{prompt}' in the current tool set.")
