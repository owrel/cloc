from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='Cloc',
    version='0.1',
    packages=find_packages(),
    install_requires=required,
    author='Owrel',
    keywords=['clingo','asp','clingotopython'],
    url="https://github.com/Owrel/cloc.git"
)