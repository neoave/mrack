format:
	black src
	black tests
	black setup.py
	isort src
	isort tests
	isort setup.py

test:
	tox
