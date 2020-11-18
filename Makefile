format:
	isort --recursive src
	isort --recursive tests
	black src
	black tests
	black setup.py

test:
	tox
