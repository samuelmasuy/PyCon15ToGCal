import os
from setuptools import setup
from pip.req import parse_requirements


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_reqs = parse_requirements('requirements.txt')

reqs = [str(install_req.req) for install_req in install_reqs]

setup(
    name = "PyCon15ToGCal",
    version = "0.0.2",
    author = "Samuel Masuy",
    author_email = "samuel.masuy@gmail.com",
    description = ("Command line application to port PyCon talks and "
                   "keynotes events to Google calendar."),
    license = "GNU General Public License version 2.0",
    packages=['PyCon15ToGCal'],
    install_requires=reqs,
    long_description=read('README.md'),
    entry_points='''
            [console_scripts]
            pycon_schedule=PyCon15ToGCal.pycon_schedule:main
    ''',
    classifiers=[
        "Topic :: Utilities",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: GNU General Public License version 2.0",
    ],
)
