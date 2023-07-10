from setuptools import setup, find_packages

setup(
    name='ccjson',
    version='0.2.0',
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