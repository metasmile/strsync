# transync
Automatically translate and synchronize '.strings' files from defined base language.


## Usage

Naturally, this tool follow [standard ISO639 1~2 codes](http://www.loc.gov/standards/iso639-2/php/English_list.php) or [apple's official document](https://developer.apple.com/library/ios/documentation/MacOSX/Conceptual/BPInternational/LanguageandLocaleIDs/LanguageandLocaleIDs.html) or [csv file](https://gist.github.com/pjc-is/49971b36db38fdeae6fc)

```
usage: transync.py [-h] [-b BASE_LANG_NAME]
                   [-x [EXCLUDING_LANG_NAMES ...]] -c
                   CLIENT_ID -s CLIENT_SECRET
                   [target path]

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
```

## Requirements

### Install

```
pip install transync
```

### About Microsoft Translation API

This tool using [Microsoft-Translator-Python-API, wrote by OpenLabs](https://github.com/openlabs/Microsoft-Translator-Python-API).

So you should do several requirements.

#### Getting your client id/secret id

Try accordance with [this explanation](https://github.com/openlabs/Microsoft-Translator-Python-API#registering-your-application)

#### Update python SSL packages

this is not required for python-2.7.9+

```shell
pip install requests[security]
```
This installs following extra packages:
```
pyOpenSSL
ndg-httpsclient
pyasn1
```


