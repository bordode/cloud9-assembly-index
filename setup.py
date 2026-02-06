from setuptools import setup, find_packages

setup(
    name="cloud9-tga",
    version="1.2.0",
    author="Dean Bordode",
    description="Temporal Geometric Assembly framework for Universal Consciousness research.",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "scikit-learn"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)
