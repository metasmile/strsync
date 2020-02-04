![](https://cdn.rawgit.com/metasmile/strsync/master/logo_1_3.svg)

[![Awesome](https://img.shields.io/badge/Awesome-iOS-red.svg)](https://github.com/vsouza/awesome-ios#localization)
[![PyPI version](https://badge.fury.io/py/strsync.svg)](https://badge.fury.io/py/strsync)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

<a href="https://www.jetbrains.com/?from=strsync"><img height="50"  src="https://www.evernote.com/l/AEFsE9xH3YVI9aqky2n5PW-clj7Q5KPyaJIB/image.png"><a/>&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://www.jetbrains.com/opensource/"><img height="54"  src="https://www.evernote.com/l/AEF0Agt6EXBGbZmKyluiDEC7N6VUPbPBNU0B/image.png"><a/>
  <a href="https://www.jetbrains.com/pycharm/"><img height="54"  src="https://www.evernote.com/l/AEGfypRW_sNDDaXWNhhhDwUajGDFcX3SR90B/image.png"></a>

*Supported by Jetbrains Open Source License Program*



----


**Automatically translate and synchronize '.strings' files from the defined base language**

<img src="https://gitcdn.xyz/cdn/metasmile/strsync/bccf2ff1cb4a4d5585460e8cfa5ffc9d9fd60b98/usage_sample.gif">

The basic concept of this python CLI tool is straightforward file name based one-way synchronizer. If you are running, other localized resources will have the same key with automatically translated strings. Of course, string on the key that already exists will not be modified at all.

![](https://github.com/metasmile/strsync/blob/master/structure.png)


## Requirements
### Install
```
pip install strsync
```

#### Enable Google Cloud Translation Python API

Set your account and authentication credentials up with Google's guide for local envirnment.

https://cloud.google.com/translate/docs/reference/libraries#client-libraries-install-python

If you can't use Translation feature, use '-w' option to copy all items from Base language.
```
$ strsync ./myapp/Resources/Localizations -w
```

#### Update Python SSL packages if needed

this is not required for python-2.7.9+

```shell
pip install requests[security]
```

## Usage

Naturally, this tool follow [standard ISO639 1~2 codes](http://www.loc.gov/standards/iso639-2/php/English_list.php) or [apple's official document](https://developer.apple.com/library/ios/documentation/MacOSX/Conceptual/BPInternational/LanguageandLocaleIDs/LanguageandLocaleIDs.html) or [this tsv table](https://github.com/metasmile/strsync/blob/master/strsync/lc_ios9.tsv)

```
usage: strsync-runner.py [-h] [-b BASE_LANG_NAME]
                         [-x EXCLUDING_LANG_NAMES [EXCLUDING_LANG_NAMES ...]]
                         [-f [FORCE_TRANSLATE_KEYS [FORCE_TRANSLATE_KEYS ...]]]
                         [-o FOLLOWING_BASE_KEYS [FOLLOWING_BASE_KEYS ...]]
                         [-w [FOLLOWING_BASE_IF_NOT_EXISTS [FOLLOWING_BASE_IF_NOT_EXISTS ...]]]
                         [-l CUTTING_LENGTH_RATIO_WITH_BASE [CUTTING_LENGTH_RATIO_WITH_BASE ...]]
                         [-c [IGNORE_COMMENTS [IGNORE_COMMENTS ...]]]
                         [-v [VERIFY_RESULTS [VERIFY_RESULTS ...]]]
                         [-s [INCLUDE_SECONDARY_LANGUAGES [INCLUDE_SECONDARY_LANGUAGES ...]]]
                         [-i [IGNORE_UNVERIFIED_RESULTS [IGNORE_UNVERIFIED_RESULTS ...]]]
                         [target path] [only for keys [only for keys ...]]

Automatically translate and synchronize .strings files from defined base
language.

positional arguments:
  target path           Target localization resource path. (root path of
                        Base.lproj, default=./)
  only for keys         Some specified keys for exclusive work. All operations
                        will work for only that keys therefore other keys will
                        be ignored. Not specified by default. (default=None)

optional arguments:
  -h, --help            show this help message and exit
  -b BASE_LANG_NAME, --base-lang-name BASE_LANG_NAME
                        A base(or source) localizable resource
                        name.(default='Base'), (e.g. "Base" via 'Base.lproj',
                        "en" via 'en.lproj')
  -x EXCLUDING_LANG_NAMES [EXCLUDING_LANG_NAMES ...], --excluding-lang-names EXCLUDING_LANG_NAMES [EXCLUDING_LANG_NAMES ...]
                        A localizable resource name that you want to exclude.
                        (e.g. "Base" via 'Base.lproj', "en" via 'en.lproj')
  -f [FORCE_TRANSLATE_KEYS [FORCE_TRANSLATE_KEYS ...]], --force-translate-keys [FORCE_TRANSLATE_KEYS [FORCE_TRANSLATE_KEYS ...]]
                        Keys in the strings to update and translate by force.
                        (input nothing for all keys.)
  -o FOLLOWING_BASE_KEYS [FOLLOWING_BASE_KEYS ...], --following-base-keys FOLLOWING_BASE_KEYS [FOLLOWING_BASE_KEYS ...]
                        Keys in the strings to follow from "Base.
  -w [FOLLOWING_BASE_IF_NOT_EXISTS [FOLLOWING_BASE_IF_NOT_EXISTS ...]], --following-base-if-not-exists [FOLLOWING_BASE_IF_NOT_EXISTS [FOLLOWING_BASE_IF_NOT_EXISTS ...]]
                        With this option, all keys will be followed up with
                        base values if they does not exist.
  -l CUTTING_LENGTH_RATIO_WITH_BASE [CUTTING_LENGTH_RATIO_WITH_BASE ...], --cutting-length-ratio-with-base CUTTING_LENGTH_RATIO_WITH_BASE [CUTTING_LENGTH_RATIO_WITH_BASE ...]
                        Keys in the float as the ratio to compare the length
                        of "Base"
  -c [IGNORE_COMMENTS [IGNORE_COMMENTS ...]], --ignore-comments [IGNORE_COMMENTS [IGNORE_COMMENTS ...]]
                        Allows ignoring comment synchronization.
  -v [VERIFY_RESULTS [VERIFY_RESULTS ...]], --verify-results [VERIFY_RESULTS [VERIFY_RESULTS ...]]
                        Verify translated results via reversed results
  -s [INCLUDE_SECONDARY_LANGUAGES [INCLUDE_SECONDARY_LANGUAGES ...]], --include-secondary-languages [INCLUDE_SECONDARY_LANGUAGES [INCLUDE_SECONDARY_LANGUAGES ...]]
                        Include Additional Secondary Languages. (+63 language
                        codes)
  -i [IGNORE_UNVERIFIED_RESULTS [IGNORE_UNVERIFIED_RESULTS ...]], --ignore-unverified-results [IGNORE_UNVERIFIED_RESULTS [IGNORE_UNVERIFIED_RESULTS ...]]
                        Allows ignoring unverified results when appending
                        them.
```

### Examples to use
```
~/Documents/myapp/myapp/Resources/Localizations$ strsync
~/Documents/myapp/myapp/Resources/Intents$ strsync
```

Define specific path you want. A parent path of *.lproj(s).
```
$ strsync ./myapp/Resources/Localizations
$ strsync ./myapp/Resources/Intents
```

Copy all items from Base language without translation.
```
$ strsync ./myapp/Resources/Localizations -w
```

All operations will work for only keys "exclusive key1" "exclusive key2" "exclusive key3". Other keys will be ignored.
```
$ strsync ./myapp/Resources/Localizations "exclusive key1" "exclusive key2" "exclusive key3"
```

Excluding japanese, spanish, finnish
```
$ strsync ./myapp/Resources/Localizations -x ja es fi
```

Forcefully translate and update by specific keys you want.
```
$ strsync -f Common.OK Common.Undo "Key name which contains white space"
```

Forcefully translate and update by All keys.
```
$ strsync -f  (input nothing)
```

When you want to accept the values in the 'Base'.
```
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
```

If you add an option **-v** or **--verify-results**,
String similarity of the reversed translation result for each language will be displayed.

```
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
```

or if you add **--ignore-unverified-results** *[Integer, Percentage (0~100) (default=0)]*,
If the similarity of each reversed translation result is under the given value, that string will be skipped(ignored).

ex)
```
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
```


## Utilities

There are some additional scripts to help your workflow with strsync.

https://github.com/metasmile/strsync/tree/master/utils
