
clear:
	find . | grep --regexp '.pyc$$' | xargs rm
	rm -rf build

upload: pypi

pypi:
	python setup.py register sdist bdist_wheel upload -r pypi
