.PHONY: tests install run

run:
	python -m piclin --help

install:
	pip install -e .

tests:
	python -m pytest tests --cov=./piclin

ubuntu_deps:
	sudo apt install mingw-w64
