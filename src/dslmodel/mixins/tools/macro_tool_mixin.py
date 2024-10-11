from typing import List, Optional, Callable
from pydantic import Field

from dslmodel.mixins.tools import Tool, ToolMixin


class MacroToolMixin(ToolMixin):
    """Mixin for macro tools."""


def main():
    """Main function"""
    from dslmodel import init_lm, init_instant, init_text
    init_instant()


if __name__ == '__main__':
    main()
