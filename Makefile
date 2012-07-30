
clear:
	find . | grep --regexp '.pyc$$' | xargs rm

upload: pypi

pypi:
	python setup.py register sdist upload
