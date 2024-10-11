from dslmodel.mixins.tools import ToolMixin


class MetaToolMixin(ToolMixin):
    """Mixin for meta tools."""


def main():
    """Main function"""
    from dslmodel import init_instant

    init_instant()


if __name__ == "__main__":
    main()
