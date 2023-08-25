from setuptools import find_packages, setup

with open("VERSION") as version_file:
    version = version_file.read().strip()

install_requires = [
    "click>=8.1.0,<9",
    "bump2version>=1.0.1,<2",
    "urllib3<2",
    "docker>=5.0.0,<6",
    "black",
    "pylint"
]
tests_require = [
    "pytest",
]

setup(
    name="forj",
    version=version,
    author="Elliot Rivers",
    description="Elliot's build and workflow tools",
    # include_package_data=True,
    packages=find_packages(
        exclude=("*.tests", "*.tests.*", "tests.*", "tests", "examples")
    ),
    python_requires=">=3.7",
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={"test": tests_require},
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        "console_scripts": {"forj=forj.cli:main"},
    },
)
