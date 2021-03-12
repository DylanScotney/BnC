
from setuptools import setup, find_packages

setup(

    name="Butter & Crust",
    author="Butter & Crust",
    version="1.2.4.1",
    description="Package to process weekly customer orders",
    packages=find_packages(exclude=['*tests', '*testing']),
    install_requires=[
        'pandas',
        'argparse',
        'django',
        'pdfkit'
        ],
    package_data={'': ['*.png']},
    tests_require=[
        ],
    entry_points={
        'console_scripts': [
            'BnC-process-orders=ButterAndCrust.ConsoleScripts.ProcessOrders:main',
            'BnC-packing-slips=ButterAndCrust.ConsoleScripts.GeneratePackingSlips:main',
            'BnC-get-database=ButterAndCrust.ConsoleScripts.DatabaseToCSV:main'
        ],
    }
)
