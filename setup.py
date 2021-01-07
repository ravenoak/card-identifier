from setuptools import setup, find_packages

setup(
    name='card_identifier',
    version='0.1.0',
    packages=find_packages(include=['card_identifier', 'card_identifier.*']),
    install_requires=[
        'click>=7.1.2',
        'Pillow>=8.0.1',
        'pokemontcgsdk>=2.0.0', ],
)
