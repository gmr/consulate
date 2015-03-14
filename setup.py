from setuptools import setup
import sys

install_requires = ['requests>=2.0.0,<3.0.0']

if sys.version_info < (2, 7, 0):
    install_requires.append('argparse')

setup(name='consulate',
      version='0.4.0',
      description="A Client library for the Consul",
      maintainer="Gavin M. Roy",
      maintainer_email="gavinr@aweber.com",
      url="https://consulate.readthedocs.org",
      install_requires=install_requires,
      license='BSD',
      package_data={'': ['LICENSE', 'README.rst']},
      packages=['consulate', 'consulate.api'],
      entry_points=dict(console_scripts=['consulate=consulate.cli:main']),
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: Implementation :: CPython',
                   'Programming Language :: Python :: Implementation :: PyPy',
                   'Topic :: System :: Systems Administration',
                   'Topic :: System :: Clustering',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Software Development :: Libraries'],
      zip_safe=True)
