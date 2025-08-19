.PHONY: tests install run

run:
	python -m shellcode_compiler --help

install:
	pip install -e .

tests:
	python -m pytest tests --cov=./shellcode_compiler

ubuntu_deps:
	sudo apt install mingw-w64
