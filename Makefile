format:
	black src
	black tests
	black setup.py
	isort src
	isort tests
	isort setup.py

test:
	tox

rpms:
	mkdir -p ~/rpmbuild/SOURCES
	mkdir -p dist
	python3 setup.py sdist
	cp dist/mrack-*.tar.gz ~/rpmbuild/SOURCES/
	rpmbuild -ba mrack.spec
	ls ~/rpmbuild/RPMS/noarch

clean-rpms:
	rm -rf ~/rpmbuild/BUILD/*
	rm -rf ~/rpmbuild/BUILDROOT/*
	rm -rf ~/rpmbuild/RPMS/*
	rm -rf ~/rpmbuild/SOURCES/*
	rm -rf ~/rpmbuild/SRPMS/*
	rm -rf ./dist
