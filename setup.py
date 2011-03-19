from setuptools import setup, find_packages

setup(
    name="peppersalt",
    version="0.0",
    author="Atsushi Odagiri",
    author_email="aodagx@gmail.com",
    packages=find_packages(),
    install_requires=[
        "zope.component",
        "argparse",
        "venusian",
    ],
    entry_points={
        "console_scripts":[
            "peppersalt=peppersalt:main",
        ],
        "peppersalt.tasks":[
            "basic_tasks=peppersalt.tasks",
        ],
    },
)
