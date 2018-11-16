from setuptools import setup, find_packages

setup(
    name = 'apache-replay',
    version = '0.0.1rc1',
    url = 'https://github.com/danizen/apache-replay.git',
    author = 'Daniel Davis',
    author_email = 'dan@danizen.net',
    description = 'Facilitates replaying of Apache files in Common Log and Combined Log format',
    packages = find_packages(),
    entry_points={
        'console_scripts': [
            'apache-replay=apache_replay.cli:main',
        ]
    },
    install_requires = ['attrs', 'requests'],
    tests_require = ['attrs', 'requests', 'pytest', 'pytest-pythonpath', 'pytest-cov']
)
