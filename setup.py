
from setuptools import setup, find_packages

setup(

    name="Butter & Crust",
    author="Butter & Crust",
    version="1.2.3",
    description="Package to process weekly customer orders",
    packages=find_packages(exclude=['*tests', '*testing']),
    install_requires=[
        'pandas',
        'argparse',
        'django',
        'pdfkit'
        ],
    tests_require=[
        ],
    entry_points={
        'console_scripts': [
            'BnC-process-orders=ConsoleScripts.OrderProcessor:main',
            'BnC-packing-slips=ConsoleScripts.GeneratePackingSlips:main',
            'BnC-get-database=ConsoleScripts.DatabaseToCSV:main'
        ]
    }
)
