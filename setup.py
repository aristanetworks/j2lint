import setuptools
from j2lint import __author__, __license__, NAME, VERSION, DESCRIPTION

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=NAME,
    version=VERSION,
    author="Manuwela Kanade",
    author_email="manuwela.kanade@gslab.com",
    description=DESCRIPTION.split("\n")[0],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aristanetworks/j2lint.git",
    project_urls={
        "Bug Tracker": "https://github.com/aristanetworks/j2lint/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    entry_points={
        "console_scripts": [
            "j2lint = j2lint.cli:run",
        ]
    },
    install_requires=[
        "jinja2",
    ],
    python_requires=">=3.6",
    keywords=["jinja", "jinja2", "lint", "linter"],
    zip_safe=False,
    include_package_data=True,
)
