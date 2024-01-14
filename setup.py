from setuptools import setup, find_packages
from codecs import open

about = {}
with open('src/__meta__.py', 'r', 'utf-8') as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    license=about['__license__'],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'orjson'
    ],
    entry_points={
        'console_scripts': [
            'ccjson = src.command:cli',
        ],
    },
)