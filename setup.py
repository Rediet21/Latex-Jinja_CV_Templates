from setuptools import setup, find_packages

setup(
    name='leap-cv',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'leap=leap.leap:main',  # Ensure this matches your module and function
        ],
    },
    package_data={
        'leap': ['templates/*.cls' ,# Include all .cls files in the templates directory
                'fonts/*',  # Include all files in the fonts directory
                ],
    },
    include_package_data=True,
)
