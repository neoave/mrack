format:
	black src
	black tests
	black setup.py

test:
	tox