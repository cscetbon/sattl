import click
import os
from sattl.test_case import TestCase


@click.command()
@click.option("--domain", required=True, type=str)
@click.option("--test-case", is_flag=True)
@click.option("--is-prod", is_flag=True)
@click.argument("path", required=True, type=click.Path(readable=True))
@click.version_option()
def run(domain, test_case, path, is_prod):
    """Sattl runs a test suite against SF"""
    if is_prod:
        click.confirm('You chose to run against prod, is that really what you want?', abort=True)
    test_case_dirs = os.listdir(path) if not test_case else [path]
    for test_case_dir in test_case_dirs:
        test_case = TestCase(path=test_case_dir, domain=domain, is_sandbox=not is_prod).setup()
        test_case.run()


if __name__ == '__main__':
    run()