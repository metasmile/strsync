# -*- coding: utf-8 -*-
"""
    transync - Automatically translate and synchronize .strings files from defined base language.
    Copyright (c) 2015 metasmile cyrano905@gmail.com (github.com/metasmile)

    repo : https://github.com/metasmile/transync
"""
import codecs
from setuptools import setup

setup(
    name="transync",
    version="1.0.2",
    packages=[
        'transync',
    ],
    entry_points = {
        "console_scripts": ['transync = transync.transync:main']
    },
    author="Metasmile @ StellarStep, Inc.",
    author_email="cyrano905@gmail.com",
    description="transync - Automatically translate and synchronize localizable resource files from defined base language for Xcode.",
    long_description=codecs.open(
        'README.rst', encoding='UTF-8'
    ).read(),
    license="MIT",
    keywords="translation microsoft transync strings localizable l10n i18n ios xcode osx mac",
    url="https://github.com/metasmile/transync",
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
        'localizable',
        'requests >= 1.2.3',
        'six',
    ]
)
