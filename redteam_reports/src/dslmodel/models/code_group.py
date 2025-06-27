# models/code_block_model.py
from pathlib import Path

from dslmodel import DSLModel
from pydantic import Field
from typing import Optional

from dslmodel.generators import gen_list
from dslmodel.models.code_block import CodeBlock


class CodeGroup(DSLModel):
    """Represents a group of code blocks."""
    blocks: list[CodeBlock] = Field([])


def main():
    """Main function"""
    from dslmodel import init_lm, init_instant, init_text
    init_text()
    lst = gen_list("Names of 10 Cracking the Coding Interview Challenges")

    group = CodeGroup.from_prompt("Python source code for " + str(lst))
    print(group.to_yaml())
    Path("ctci.yaml").write_text(group.to_yaml())


if __name__ == '__main__':
    main()
