from setuptools import setup, find_packages

setup(
    name="sgui",
    version="0.0.7",
    packages=find_packages(),
    install_requires=[
        "raylib>=5.0.0"
    ],
    author="Elis Eriksson",
    author_email="elis.eriksson.2010@gmail.com",
    description="Lightweight and easy-to-use Immediate Mode GUI library for Python and Raylib",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/spelis/sgui",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
