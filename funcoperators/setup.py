# from distutils.core import setup
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

import re
def get_property(prop, project):
    with open(project + '/__init__.py') as f:
        return re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format(prop), f.read()).group(1)

setup(
    name='funcoperators',
    version=get_property('__version__', 'funcoperators'),
    description='Allow natural function notations like (1,2) /dot/ (3,4) for dot((1,2), (3,4)) or 1 /frac/ 3 for Fraction(1,3), pipes and other useful operators to functions.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Robert Vanden Eynde',
    author_email='robertvandeneynde@hotmail.com',
    packages=['funcoperators'], # setuptools.find_packages() 'mymath.adv'
    url='https://github.com/robertvandeneynde/python',
)
