from setuptools import find_packages
from setuptools import setup


setup(
	name='barlow',
	version='1.0.0',
	description='Clarence Barlow in Memoriam',
	author='Amir Teymuri',
	author_email='amiratwork22@gmail.com',
	# packages=['barlow'],
    packages=find_packages('src'),
    package_dir={'': 'src'},
)

