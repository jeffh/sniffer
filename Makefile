
upload: pypi

pypi:
	python setup.py register sdist upload

clear:
	find . | grep --regexp '.pyc$' | xargs rm
