"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Oh_Gee_Em."""


if __name__ == "__main__":
    main(prog_name="oh_gee_em")  # pragma: no cover
