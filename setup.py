from setuptools import setup


VERSION = "0.0.1"

setup(
    name='text-analyze',
    description="",
    version=VERSION,
    url='https://github.com/KokocGroup/text-analyze4',
    download_url='https://github.com/KokocGroup/google-parser/tarball/v{}'.format(VERSION),
    packages=['text-analyze'],
    package_dir={'text-analyze': 'text_analyze'},
    package_data={'text-analyze': ['text_analyze/data/*']},
    install_requires=[
        'python-cdb==0.35',
        'nltk==3.0.0',
        'pymorphy2==0.8',
        'lxml==3.4.4',
        'beautifulsoup4==4.3.2',
    ],
)
