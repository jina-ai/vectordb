from setuptools import setup, find_packages
from vectordb import __version__

# Read the contents of requirements.txt
with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='vectordb',
    version=__version__,
    description='The Python VectorDB. Build your vector database from working as a library to scaling as a database in the cloud',
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    extras_require={
        'test': [
            'pytest',
            'pytest-asyncio',
            'monkeypatch'
        ],
    },
    install_requires=requirements,
)
