# mypy: ignore-errors
from pathlib import Path

from setuptools import setup

readme = Path("README.rst").read_text(encoding="utf-8")
version = Path("pyswan/_version.py").read_text(encoding="utf-8")
about = {}
exec(version, about)

setup(
    name="pyswan",
    version=about["__version__"],
    description="Better dates & times & numbers for Python of Chinese",
    long_description=readme,
    long_description_content_type="text/x-rst",
    url="https://github.com/JosiahMg/pyswan",
    author="Josiah Meng",
    author_email="josiahmg@163.com",
    license="Apache 2.0",
    packages=["pyswan"],
    package_data={"pyswan": ["py.typed"]},
    zip_safe=False,
    python_requires=">=3.6",
    install_requires=[
        "arrow>=1.1.0",
        "typing_extensions; python_version<'3.9'",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="pyswan Chinese date time",
    project_urls={
        "Repository": "https://github.com/JosiahMg/pyswan",
        "Bug Reports": "https://github.com/JosiahMg/pyswan/issues",
        "Documentation": "https://github.com/JosiahMg/pyswan",
    },
)
