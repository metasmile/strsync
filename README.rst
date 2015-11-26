.. contents::
   :depth: 3
..

.. figure:: https://cdn.rawgit.com/metasmile/strsync/master/logo.svg
   :alt:

Automatically translate and synchronize '.strings' files from defined
base language.

The basic concept of this tool is simple file name based one-way
synchronizer. While the actual translation work, My biggest desire was
to just fill an empty strings easily. In a normal project, automatic
translation is sufficient. Because They are always simple sentences.
Yes, No, Do it, Not agree, etc..

If you are running, other localized resources will have exactly the same
key with automatically translated strings. Of course, String on the key
that already exists will not be modified at all.

.. figure:: https://github.com/metasmile/metasmile.github.io/blob/master/static/strsync/desc1.png
   :alt:

Requirements
============

Install
-------

::

    pip install strsync

Getting your client id/secret id to use Microsoft Translation API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Try accordance with `this
explanation <https://msdn.microsoft.com/en-us/library/mt146806.aspx>`__

Update Python SSL packages if needed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

this is not required for python-2.7.9+

.. code:: shell

    pip install requests[security]

Usage
=====

Naturally, this tool follow `standard ISO639 1~2
codes <http://www.loc.gov/standards/iso639-2/php/English_list.php>`__ or
`apple's official
document <https://developer.apple.com/library/ios/documentation/MacOSX/Conceptual/BPInternational/LanguageandLocaleIDs/LanguageandLocaleIDs.html>`__
or `csv file <https://gist.github.com/pjc-is/49971b36db38fdeae6fc>`__

::

    usage: strsync    [-h] [-b BASE_LANG_NAME]
                       [-x [EXCLUDING_LANG_NAMES ...]] -c
                       CLIENT_ID -s CLIENT_SECRET
                       [-f [FORCE_TRANSLATE_KEYS ...]]
                       [target path]

    Automatically translate and synchronize .strings files from defined base
    language.

    positional arguments:
      target path           Target localizable resource path. (root path of
                            Base.lproj, default=./)

    optional arguments:
      -h, --help            show this help message and exit
      -b BASE_LANG_NAME, --base-lang-name BASE_LANG_NAME
                            A base(or source) localizable resource
                            name.(default='Base'), (e.g. "Base" via 'Base.lproj',
                            "en" via 'en.lproj')
      -x [EXCLUDING_LANG_NAMES ...], --excluding-lang-names [EXCLUDING_LANG_NAMES ...]
                            A localizable resource name that you want to exclude.
                            (e.g. "Base" via 'Base.lproj', "en" via 'en.lproj')
      -c CLIENT_ID, --client-id CLIENT_ID
                            Client ID for MS Translation API
      -s CLIENT_SECRET, --client-secret CLIENT_SECRET
                            Client Secret key for MS Translation API
      -f [FORCE_TRANSLATE_KEYS ...], --force-translate-keys [FORCE_TRANSLATE_KEYS ...]
                            Keys in the strings to update and translate by force.

Examples to use
---------------

::

    $ strsync -c clien_idXXXX -s clien_secretXXXX

Define specific path you want.

::

    $ strsync ./myXcodeProj/Resources/Localizations -c clien_idXXXX -s clien_secretXXXX

Excluding japanese, spanish, finnish

::

    $ strsync ./myXcodeProj/Resources/Localizations -c clien_idXXXX -s clien_secretXXXX -x ja es fi

Forcefully translate and update by specific keys you want.

::

    $ strsync -c clien_idXXXX -s clien_secretXXXX -f Common.OK Common.Undo


Forcefully translate and update by specific keys you want.

::

    $ strsync -c clien_idXXXX -s clien_secretXXXX -f   (input nothing.)


When you want to accept the values in the 'Base'.

::

    $ strsync -c clien_idXXXX -s clien_secretXXXX -fb autoenhance flashmode

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
