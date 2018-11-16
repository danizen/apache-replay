from setuptools import setup


def get_readme():
    with open('README.md') as f:
        return f.read()


setup(
    name = 'apache-replay',
    version = '0.0.2',
    url = 'https://github.com/danizen/apache-replay.git',
    author = 'Daniel Davis',
    author_email = 'dan@danizen.net',
    description = 'Facilitates replaying of Apache files in Common Log and Combined Log format',
    long_description = get_readme(),
    long_description_content_type='text/markdown; charset=UTF-8; variant=CommonMark',
    packages = ['apache_replay'],
    entry_points={
        'console_scripts': [
            'apache-replay=apache_replay.cli:main',
        ]
    },
    install_requires = ['attrs', 'requests'],
    tests_require = ['attrs', 'requests', 'pytest', 'pytest-pythonpath', 'pytest-cov', 'tox'],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
