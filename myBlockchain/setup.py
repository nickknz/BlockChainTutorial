from setuptools import setup


setup(
    name="blockchain_poc",
    version="0.1.0",
    author="Daniel Perez",
    author_email="daniel@perez.sh",
    packages=["blockchain_poc"],
    install_requires=[
        "ecdsa",
    ],
    extras_require={
        "dev": [
            "pytest",
            "hypothesis",
        ]
    },
    entry_points={
        "console_scripts": [
            "blockchain-poc=blockchain_poc.cli:main",
        ]
    },
)
