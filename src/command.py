import click
import sys
from os import path
from src.reader import *
from src.parser import Parser
from src.writer import Writer


def run(parser: Parser, writer: Writer):
    """解析流程"""
    # while(parser.parseable):
    #     item = parser.parseline()
    #     if(len(item) > 0):
    #         writer.write(item)
    with click.progressbar(
        parser,
        label="Please wait a bit",
        show_percent=True,
        show_eta=True,
        show_pos=True,
        color=True,
        item_show_func=lambda a: "" if not a else "parsing" 
    ) as bar:
        for item in bar:
            if item:
                writer.write(item)
    writer.flush()


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(
    context_settings=CONTEXT_SETTINGS,
    epilog="Check out our docs at https://click.palletsprojects.com/ for more details",
)
@click.option(
    "-p",
    "--parse",
    "infile",
    type=click.STRING,
    help="Build log file to parse compilation commands from." + "(Default: stdin)",
    required=False,
    default="-",
)

@click.option(
    "-d",
    "--dir",
    "build_dir",
    type=click.STRING,
    help="Specifies the build path for current project." + "(Default: current working direcoty)",
    required=False,
    default="",
)
def cli(infile, build_dir):
    """generate a compilation database for make-based build systems.

    \b
    features:
    1. Support for redundent build systems that use shell scripts to nest make.
    2. Simpler to use than similiar tools without losing compilation information.
    3. Open source, you can modify it according to the actual build situation.
    """
    # click.echo(infile)
    if infile == "-":
        run(parser=Parser(reader=StdinReader(), build_dir=build_dir), writer=Writer())
    elif path.isfile(infile):
        run(parser=Parser(reader=FileReader(infile), build_dir=build_dir), writer=Writer())
    else:
        click.echo(f"Unexpected file name: {click.format_filename(infile)}")

    # click.echo("end of here")


if __name__ == "__main__":
    # parserdemo = Parser(reader=FileReader("read.txt"))
    # writerdemo = Writer()
    # run(parser=parser, writer=writer)
    cli()
    # print(sys.path)
