from dslmodel.mixins.tools import ToolMixin


class MacroToolMixin(ToolMixin):
    """Mixin for macro tools."""


def main():
    """Main function"""
    from dslmodel import init_instant

    init_instant()


if __name__ == "__main__":
    main()
