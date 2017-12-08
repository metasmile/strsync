[AD] Meet our app using stringsync, Elie - Your next mobile photography
assistant. http://elie.cam

.. figure:: https://cdn.rawgit.com/metasmile/strsync/master/logo_1_3.svg
   :alt: 

|Awesome| |PyPI version| |License|

Automatically translate and synchronize '.strings' files from the
defined base language.

The basic concept of this python CLI tool is straightforward file name
based one-way synchronizer. If you are running, other localized
resources will have the same key with automatically translated strings.
Of course, string on the key that already exists will not be modified at
all.

While the actual i18n work, my biggest desire was to just quickly fill
many empty strings first. This tool has been made for that purpose. In a
normal project, automatic translation is sufficient. Because They are
always simple sentences. Yes, No, Do it, Not agree, etc.. As you know
all translation results of this tool is just based on the Google
Translator. Stringsync uses unofficial google ajax translation APIs. So
no account and API key is required. And please note that, in case of
more complex, inspections by human will be required for exact results.
But you may save very much of your time!

.. figure:: https://github.com/metasmile/strsync/blob/master/structure.png
   :alt: 

Requirements
------------

Install
~~~~~~~

::

    pip install strsync

Update Python SSL packages if needed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

this is not required for python-2.7.9+

.. code:: shell

    pip install requests[security]

Usage
-----

Naturally, this tool follow `standard ISO639 1~2
codes <http://www.loc.gov/standards/iso639-2/php/English_list.php>`__ or
`apple's official
document <https://developer.apple.com/library/ios/documentation/MacOSX/Conceptual/BPInternational/LanguageandLocaleIDs/LanguageandLocaleIDs.html>`__
or `this tsv
table <https://github.com/metasmile/strsync/blob/master/strsync/lc_ios9.tsv>`__

::

    usage: strsync <target localization resource path>

    Automatically translate and synchronize .strings files from defined base language.

    positional arguments:
      target path           Target localization resource path. (root path of
                            Base.lproj, default=./)

    optional arguments:
      -h, --help            show this help message and exit
      -b, --base-lang-name BASE_LANG_NAME
                            A base(or source) localizable resource
                            name.(default='Base'), (e.g. "Base" via 'Base.lproj',
                            "en" via 'en.lproj')
      -x, --excluding-lang-names [EXCLUDING_LANG_NAMES ...]
                            A localizable resource name that you want to exclude.
                            (e.g. "Base" via 'Base.lproj', "en" via 'en.lproj')
      -f, --force-translate-keys [FORCE_TRANSLATE_KEYS ...]
                            Keys in the strings to update and translate by force.
      -o, --following-base-keys [FOLLOWING_BASE_KEYS ...]
                            Keys in the strings to follow from "Base".
      -l, --following-base-keys-if-length-longer
                            Keys in the strings to follow from "Base"
                            if its length longer than the length of "Base" value.
      -c, --ignore-comments
                            Allows ignoring comment synchronization.
      -v, --verify-results [VERIFY_RESULTS [VERIFY_RESULTS ...]]
                            Verify translated results via reversed results
      -i, --ignore-unverified-results [IGNORE_UNVERIFIED_RESULTS [IGNORE_UNVERIFIED_RESULTS ...]]
                            Allows ignoring unverified results when appending them.

Examples to use
~~~~~~~~~~~~~~~

::

    ~/Documents/myapp/myapp/Resources/Localizations$ strsync

Define specific path you want.

::

    $ strsync ./myapp/Resources/Localizations

Excluding japanese, spanish, finnish

::

    $ strsync ./myapp/Resources/Localizations -x ja es fi

Forcefully translate and update by specific keys you want.

::

    $ strsync -f Common.OK Common.Undo "Key name which contains white space"

Forcefully translate and update by All keys.

::

    $ strsync -f  (input nothing)

When you want to accept the values in the 'Base'.

::

    $ strsync -o autoenhance flashmode

    #before
    "flashmode" = "وضع الفلاش";
    "flashmode.auto" = "السيارات";
    "flashmode.on" = "على";
    "autoenhance" = "تعزيز السيارات";

    #after
    "flashmode" = "Flash Mode";
    "flashmode.auto" = "السيارات";
    "flashmode.on" = "على";
    "autoenhance" = "Auto-Enhance";

If you add an option **-v** or **--verify-results**, String similarity
of the reversed translation result for each language will be displayed.

::

    $ strsync (...) -v

    el
      Hi: Hi -> Γεια σου -> Hi, Matched: 100%
    fr-CA
      Hi: Hi -> Salut -> Hello, Matched: 50%
    id
      Hi: Hi -> Hai -> Two, Matched: 0%
    fr
      Hi: Hi -> Salut -> Hello, Matched: 50%
    uk
      Hi: Hi -> Привіт -> Hi, Matched: 100%
    hr
      Hi: Hi -> Bok -> Book, Matched: 0%
    da
      Hi: Hi -> Hej -> Hi, Matched: 100%
    ja
      Hi: Hi -> こんにちは -> Hello, Matched: 50%
    he
      Hi: Hi -> היי -> Hey, Matched: 50%
    ko
      Hi: Hi -> 안녕 -> Hi, Matched: 100%
    sv
      Hi: Hi -> Hej -> Hi, Matched: 100%
    es-MX
      Hi: Hi -> Hola -> Hello, Matched: 50%
    sk
      Hi: Hi -> ahoj -> Hi, Matched: 100%
    zh-CN
      Hi: Hi -> 你好 -> How are you doing, Matched: 50%

or if you add **--ignore-unverified-results** *[Integer, Percentage
(0~100) (default=0)]*, If the similarity of each reversed translation
result is under the given value, that string will be skipped(ignored).

ex)

::

    strings will be skipped if its text similarity from reversed translation result is under 50

    $ strsync (...) --ignore-unverified-results 50

    el
      Hi: Hi -> Γεια σου -> Hi, Matched: 100%
    fr-CA
      (Ignored) Hi: Hi -> Salut -> Hello, Matched: 50%
    id
      (Ignored) Hi: Hi -> Hai -> Two, Matched: 0%
    fr
      (Ignored) Hi: Hi -> Salut -> Hello, Matched: 50%
    uk
      Hi: Hi -> Привіт -> Hi, Matched: 100%
    hr
      (Ignored) Hi: Hi -> Bok -> Book, Matched: 0%
    da
      Hi: Hi -> Hej -> Hi, Matched: 100%
    ja
      (Ignored) Hi: Hi -> こんにちは -> Hello, Matched: 50%
    he
      (Ignored) Hi: Hi -> היי -> Hey, Matched: 50%
    ko
      Hi: Hi -> 안녕 -> Hi, Matched: 100%
    sv
      Hi: Hi -> Hej -> Hi, Matched: 100%
    es-MX
      (Ignored) Hi: Hi -> Hola -> Hello, Matched: 50%
    sk
      Hi: Hi -> ahoj -> Hi, Matched: 100%
    zh-CN
      (Ignored) Hi: Hi -> 你好 -> How are you doing, Matched: 50%

.. |Awesome| image:: https://cdn.rawgit.com/sindresorhus/awesome/d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg
   :target: https://github.com/vsouza/awesome-ios#localization
.. |PyPI version| image:: https://badge.fury.io/py/strsync.svg
   :target: https://badge.fury.io/py/strsync
.. |License| image:: https://img.shields.io/pypi/l/strsync.svg
   :target: http://img.shields.io/badge/license-MIT-lightgrey.svg?style=flat
