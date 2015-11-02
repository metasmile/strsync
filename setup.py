# -*- coding: utf-8 -*-
"""
    transync

    Automatically translate and synchronize '.strings' files from defined base language.

    The basic concept of this tool is simple file name based one-way synchronizer. While the actual translation work, My biggest desire was to just fill an empty strings easily. In a normal project, automatic translation is sufficient. Because They are always simple sentences. Yes, No, Do it, Not agree, etc..

    If you are running, other localized resources will have exactly the same key with automatically translated strings. Of course, String on the key that already exists will not be modified at all.

    Usage

    Naturally, this tool follow standard ISO639 1~2 codes or apple's official document or csv file

    Examples to use

    $ python transync.py -c clien_idXXXX -s clien_secretXXXX

    Define specific path you want.
    $ python transync.py ./myXcodeProj/Resources/Localizations -c clien_idXXXX -s clien_secretXXXX

    Excluding japanese, spanish, finnish
    $ python transync.py ./myXcodeProj/Resources/Localizations -c clien_idXXXX -s clien_secretXXXX -x ja es fi

    Forcefully translate and update by specific keys you want.
    $ python transync.py -c clien_idXXXX -s clien_secretXXXX -f Common.OK Common.Undo

"""
import codecs
from setuptools import setup


setup(
    name="transync",
    version="1.0",
    packages=[
        'transync',
    ],
    package_dir={
        'transync': '.'
    },
    author="Metasmile @ StellarStep, Inc.",
    author_email="cyrano905@gmail.com",
    description="transync - Automatically translate and synchronize localizable resource files from defined base language for Xcode.",
    long_description=codecs.open(
        'README.md', encoding='UTF-8'
    ).read(),
    license="MIT",
    keywords="translation microsoft transync strings localizable l10n i18n ios xcode osx mac",
    url="https://github.com/metasmile",
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Internationalization",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
    ],
    install_requires=[
        'microsofttranslator',
        'requests >= 1.2.3',
        'six',
    ]
)
