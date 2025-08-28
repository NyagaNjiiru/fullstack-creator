from setuptools import setup, find_packages

setup(
    name="fullstack-creator",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "inquirer",
    ],
    entry_points={
        "console_scripts": [
            "create-fullstack=fullstack_creator.main:main",
        ],
    },
    author="Patrick Njiru",
    description="A tool to create fullstack projects with various frameworks",
)
