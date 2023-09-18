from setuptools import setup, find_packages
from os import path
AUTHOR = 'Jina AI'
AUTHOR_EMAIL = 'hello@jina.ai'
LICENSE = 'Apache 2.0'
GITHUB_URL = 'https://github.com/jina-ai/vectordb/'
DOWNLOAD_URL = 'https://github.com/jina-ai/vectordb/tags'
try:
    pkg_name = 'vectordb'
    libinfo_py = path.join(pkg_name, '__init__.py')
    with open(libinfo_py, 'r', encoding='utf-8') as f:
        libinfo_content = f.readlines()
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
    author= AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    url=GITHUB_URL,
    download_url=DOWNLOAD_URL,
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
