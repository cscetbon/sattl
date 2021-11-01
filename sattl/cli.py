import click
import os
from sattl.test_case import TestCase
from sattl.logger import logger
from logging import DEBUG


@click.command()
@click.option("--debug", is_flag=True)
@click.option("--sf-org", required=True, type=str)
@click.option("--is-prod", is_flag=True)
@click.option("--timeout", default=30, type=int)
@click.option("--test-case", is_flag=True)
@click.argument("path", required=True, type=click.Path(readable=True))
@click.version_option()
def run(debug, sf_org, is_prod, timeout, test_case, path):
    """Sattl runs a test suite against SF"""
    if debug:
        logger.setLevel(DEBUG)
        logger.handlers[0].setLevel(DEBUG)
    if is_prod:
        click.confirm('You chose to run against prod, is that really what you want?', abort=True)
    test_case_dirs = [os.path.join(path, subdir) for subdir in os.listdir(path)] if not test_case else [path]
    for test_case_dir in test_case_dirs:
        test_case = TestCase(path=test_case_dir, sf_org=sf_org, timeout=timeout, is_prod=is_prod)
        test_case.setup()
        test_case.run()


if __name__ == '__main__':
    run()