from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='solml',
    version='0.0.1',
    description='OpenSolarMap - machine learning',
    long_description=long_description,
    url='https://github.com/opensolarmap/solml',
    author='Michel Blancard',
    author_email='michel.blancard@data.gouv.fr',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    packages=['solml'],
    install_requires=[
        'jupyter>=1',
        'pandas>=0.19',
        'numpy>=1.12',
        'matplotlib>=2',
        'GDAL>=2',
        'Pillow>=4',
        'geographiclib',
        'scikit-learn>=0.18',
        'scipy>=0.18',
        'keras>=2.0',
        'theano>=0.8',
        'tensorflow>=0.12',
        'opencv-python>=3.2',
        'h5py>=2.6',
        'psycopg2>=2.6',
        'psycopg-postgis>=0.1',
    ],
)
