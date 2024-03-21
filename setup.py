from setuptools import setup, find_packages

setup(
    name='baseball_analysis',
    version='0.1',
    packages=find_packages(),
    description='A package for baseball strike zone analysis',
    author='Your Name',
    author_email='your@email.com',
    install_requires=[
        'python-mlb-statsapi',
        'MLB-StatsAPI',
        'pybaseball',
        'pandas',
        'numpy',
        'seaborn',
        'matplotlib',
        'mlbstatsapi'
        #'pybaseball',
        #'matplotlib'
    ],
)
