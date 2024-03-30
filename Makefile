build:
	@echo "Building..."
	python -m build

install:
	@echo "Installing..."
	pip install dist/*.whl

test:
	@echo "Testing..."
	python -m unittest tests/*.py
