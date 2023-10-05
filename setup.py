from setuptools import find_packages
from setuptools import setup


setup(
	name='klarenz',
	version='1.0.0',
	description='Programmatically generate Lilypond scores, with ease and elegance of pure Python ',
	author='Amir Teymuri',
	author_email='amiratwork22@gmail.com',
	packages=['klarenz'],
    # packages=find_packages('src'),
    package_dir={'klarenz': 'src'},
)

