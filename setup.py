import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="my_repo_utils",
    version="0.0.1",
    description="A collection of personal utils interacting with my repos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SirGnip/my_repo_utils",

    # Code is in "src/", an un-importable directory (at least not easily or accidentally)
    # Helps reduce confusion around whether code from repo or site-packages is being used.
    # https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure
    # https://hynek.me/articles/testing-packaging/
    # https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],

    python_requires='>=3.7',
    install_requires=[
        # 3rd party dependencies
        "PyGithub>=1.53",
        "click>=7.1.2",
        "pytest==5.3.1",
        "pylint==2.4.4",
        "mypy==0.750",
    ],
)
