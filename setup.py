from setuptools import setup, find_packages

setup(
    name='gpx-analyzer',
    version='0.1',
    description='A cli tool to extract gpx file and generate map',
    author='PenHsuanWang',
    license='MIT',
    platforms=['unix', 'linux', 'osx', 'win32'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
    ],
    packages=find_packages(),  # Automatically discover and include all packages
    install_requires=[
        'click',
    ],
    python_requires='>=3.10',
    zip_safe=False,
    extras_require={
        'testing': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'mypy>=0.910',
            'flake8>3.9',
            'tox>=3.24',
        ]
    },
    entry_points={
        'console_scripts': [
            'gpxana=src.cli:main',
        ]
    }
)
