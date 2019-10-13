

test:
	python3 -m pytest --cov-report term-missing --cov=breathe tests/

clean:
	rm -r dist build

dist:
	python3 setup.py sdist bdist_wheel
	python27 setup.py bdist_wheel

package: dist
	twine upload dist/*
