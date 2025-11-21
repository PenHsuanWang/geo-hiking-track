from setuptools import setup, find_packages

setup(
    name='gpx-analyzer',
    version='0.1',
    description='A library and CLI tool to parse GPX files and generate interactive maps',
    author='PenHsuanWang',
    license='MIT',
    platforms=['unix', 'linux', 'osx', 'win32'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'click',
        'folium>=0.14.0',
        'numpy>=1.25.0',
        'Pillow>=9.0.0',
        'reportlab>=4.0.0',
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
            'gpxana=cli:main',
        ]
    }
)
