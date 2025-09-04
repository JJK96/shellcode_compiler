import click
import sys
from .config import settings
from . import compile as _compile, template as _template, OutputFormat, hash_djb2
from .winlib import template_winlib
import logging
logging.basicConfig(format="%(message)s", level=logging.INFO)

@click.group()
def main():
    pass

@main.command()
@click.argument("input_file")
@click.option("-o", "--output", help="Output directory", default="build")
@click.option("-f", "--output-format", help="Format of the resulting binary", type=click.Choice(OutputFormat), default=OutputFormat.BINARY)
@click.option("--rebuild", help="Delete the output directory before building", is_flag=True)
def compile(input_file, output, output_format, rebuild):
    """Compile C code to shellcode while allowing the use of Win32 APIs without changes to the source code. In addition, strings and other data can be used without special encoding like stack strings."""
    _compile(input_file=input_file, output_dir=output, output_format=output_format, rebuild=rebuild)
    

@main.command()
@click.argument("input_file")
@click.argument("data", nargs=-1)
def template(input_file, data):
    """Perform templating on the given input file"""
    context = {}
    for x in data:
        k,v = x.split('=')
        if v.startswith('@'):
            with open(v[1:], 'rb') as f:
                v = f.read()
        context[k] = v
    content = _template(input_file, context)
    sys.stdout.write(content)


@main.command()
@click.argument("input_file")
@click.argument("functions_file")
def winlib(input_file, functions_file):
    functions = []
    with open(functions_file) as f:
        for line in f:
            functions.append(line[:-1])
    content = template_winlib(input_file, functions)
    sys.stdout.write(content)


@main.command()
@click.argument("string")
def hash(string):
    """
    STRING: Module name or function name to hash
    """

    h = hash_djb2(string)
    print(hex(h))

if __name__ == "__main__":
    main()
