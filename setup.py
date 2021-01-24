
from setuptools import setup, find_packages

setup(

    name="Butter & Crust Order Processor",
    author="Butter & Crust",
    version="1.0.0",
    description="Package to process weekly customer orders",
    packages=find_packages(exclude=['*tests']),
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
            'BnC-Orders=lib.OrderProcessor:main'
        ]
    }
)
