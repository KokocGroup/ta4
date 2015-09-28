from setuptools import setup


VERSION = "0.2.5"

setup(
    name='ta4',
    description="",
    version=VERSION,
    url='https://github.com/KokocGroup/ta4',
    download_url='https://github.com/KokocGroup/ta4/tarball/v{}'.format(VERSION),
    packages=['ta4'],
    package_dir={'ta4': 'ta4'},
    package_data={'ta4': ['data/nltk/english.pickle']},
    install_requires=[
        'nltk==3.0.0',
        'pymorphy2==0.8',
        'lxml==3.4.4',
        'beautifulsoup4==4.3.2',
    ],
)
