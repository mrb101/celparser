from setuptools import setup, find_packages

setup(
    name="celparser",
    version="0.1.0",
    description="Python parser and evaluator for Google Common Expression Language (CEL)",
    author="PyCEL Team",
    author_email="hamadeh.basel@gmail.com",
    url="https://github.com/mrb101/celparser",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
)
