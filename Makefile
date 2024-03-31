build:
	@echo "Building..."
	python -m build

install:
	@echo "Installing..."
	pip install dist/*.whl --force-reinstall

test:
	@echo "Testing..."
	python -m coverage run -m unittest tests/*.py
	python -m coverage report -m
