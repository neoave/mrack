format:
	isort src
	isort tests
	black src
	black tests
	black setup.py

test:
	tox