from setuptools import setup, find_packages
from os import path

try:
    pkg_name = 'vectordb'
    libinfo_py = path.join(pkg_name, '__init__.py')
    libinfo_content = open(libinfo_py, 'r', encoding='utf-8').readlines()
    version_line = [l.strip() for l in libinfo_content if l.startswith('__version__')][
        0
    ]
    exec(version_line)  # gives __version__
except FileNotFoundError:
    __version__ = '0.0.0'

try:
    with open('README.md', encoding='utf-8') as fp:
        _long_description = fp.read()
except FileNotFoundError:
    _long_description = ''


# Read the contents of requirements.txt
with open(path.join(path.dirname(__file__), 'requirements.txt'), 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='vectordb',
    version=__version__,
    description='The Python VectorDB. Build your vector database from working as a library to scaling as a database in the cloud',
    long_description=_long_description,
    long_description_content_type='text/markdown',
    author='Jina AI',
    author_email='hello@jina.ai',
    license='Apache 2.0',
    url='https://github.com/jina-ai/vectordb/',
    download_url='https://github.com/jina-ai/vectordb/tags',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'vectordb=vectordb.__main__:vectordb',
        ],
    },
    extras_require={
        'test': [
            'pytest',
            'pytest-asyncio',
            'pytest-repeat',
            'flaky',
            'pytest-timeout'
        ],
    },
    install_requires=requirements,
)
