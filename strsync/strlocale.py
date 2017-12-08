# -*- coding: utf-8 -*-
from babel import Locale

def get_locale(locale_code):
    try:
        return Locale.parse(locale_code)
    except:
        return Locale.parse(locale_code, sep='-')
    else:
        print("Unexpected error:", sys.exc_info()[0])
        raise

def lang(locale_code):
    return get_locale(locale_code).language

def region(locale_code):
    return get_locale(locale_code).territory

def script(locale_code):
    return get_locale(locale_code).script

def is_equal_lang(locale1, local2):
    return lang(locale1)==lang(locale2)

def is_equal_lang_and_script(locale1, locale2):
    return lang(locale1)==lang(locale2) and script(locale1)==script(locale2)
