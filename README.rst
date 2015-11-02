transync
========

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

Usage
-----

Naturally, this tool follow `standard ISO639 1~2
codes <http://www.loc.gov/standards/iso639-2/php/English_list.php>`__ or
`apple's official
document <https://developer.apple.com/library/ios/documentation/MacOSX/Conceptual/BPInternational/LanguageandLocaleIDs/LanguageandLocaleIDs.html>`__
or `csv file <https://gist.github.com/pjc-is/49971b36db38fdeae6fc>`__

::

    usage: transync    [-h] [-b BASE_LANG_NAME]
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
~~~~~~~~~~~~~~~

::

    $ transync -c clien_idXXXX -s clien_secretXXXX

Define specific path you want.

::

    $ transync ./myXcodeProj/Resources/Localizations -c clien_idXXXX -s clien_secretXXXX

Excluding japanese, spanish, finnish

::

    $ transync ./myXcodeProj/Resources/Localizations -c clien_idXXXX -s clien_secretXXXX -x ja es fi

Forcefully translate and update by specific keys you want.

::

    $ transync -c clien_idXXXX -s clien_secretXXXX -f Common.OK Common.Undo

Requirements
------------

Install
~~~~~~~

::

    pip install transync

Using Microsoft Translation API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This tool using `Microsoft-Translator-Python-API, wrote by
OpenLabs <https://github.com/openlabs/Microsoft-Translator-Python-API>`__.

So you should do several processes by requirements.

Getting your client id/secret id
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Try accordance with `this
explanation <https://github.com/openlabs/Microsoft-Translator-Python-API#registering-your-application>`__

Update python SSL packages
^^^^^^^^^^^^^^^^^^^^^^^^^^

this is not required for python-2.7.9+

.. code:: shell

    pip install requests[security]

This installs following extra packages:

::

    pyOpenSSL
    ndg-httpsclient
    pyasn1
