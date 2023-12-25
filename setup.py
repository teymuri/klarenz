from setuptools import setup


setup(
	name = 'klarenz',
	# version = '0.0.5',
	description = 'Programmatically generate Lilypond scores, with ease and elegance of pure Python ',
	author = 'Amir Teymuri',
	author_email = 'amiratwork22@gmail.com',
	packages = ['klarenz'],
    package_dir = {'klarenz': 'src/klarenz'},
    url = 'https://github.com/teymuri/klarenz.git',
    python_requires = ">=3.5",
)

