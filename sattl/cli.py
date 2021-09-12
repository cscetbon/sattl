import click


@click.command()
@click.option("--org", required=True, type=str)
@click.option("--is-sandbox", default=True, type=bool)
@click.argument("path", required=True, type=click.Path())
@click.version_option()
def run(org, path, is_sandbox):
    """Sattl runs a test suite against SF"""
    check_is_sandbox(is_sandbox)


def check_is_sandbox(is_sandbox):
    pass


if __name__ == '__main__':
    run()