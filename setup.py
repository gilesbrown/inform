"""A client library for self-describing RESTful web services.

"""

from setuptools import setup

setup(
    name="Inform",
    description=__doc__,
    version="0.1",
    author="Giles Brown",
    author_email="giles@milo.com",
    packages=['inform'],
    requires=[
        'requests (>=2.0)'
    ],
    test_requires=[
        'itty',
        'mako',
    ]
)
