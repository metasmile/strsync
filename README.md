# transync
Automatically translate and synchronize '.strings' files from defined base language.


## Usage

Naturally, this tool follow [standard ISO639 1~2 codes](http://www.loc.gov/standards/iso639-2/php/English_list.php) or [apple's official document](https://developer.apple.com/library/ios/documentation/MacOSX/Conceptual/BPInternational/LanguageandLocaleIDs/LanguageandLocaleIDs.html) or [csv file](https://gist.github.com/pjc-is/49971b36db38fdeae6fc)

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


