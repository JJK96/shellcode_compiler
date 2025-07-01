import click
from .config import settings
from . import compile as _compile, template as _template, OutputFormat, hash_djb2
import logging
logging.basicConfig(format="%(message)s", level=logging.INFO)

@click.group()
def main():
    pass

@main.command()
@click.argument("input_file")
@click.option("-o", "--output", help="Output directory", default="build")
@click.option("-f", "--output-format", help="Format of the resulting binary", type=click.Choice(OutputFormat))
def compile(input_file, output, output_format):
    """Compile C code to shellcode while allowing the use of Win32 APIs without changes to the source code. In addition, strings and other data can be used without special encoding like stack strings."""
    _compile(input_file=input_file, output_dir=output, output_format=output_format)
    

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
    _template(input_file, context)


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
