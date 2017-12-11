# -*- coding: utf-8 -*-
from babel import Locale

def get_locale(locale_code):
    try:
        return Locale.parse(locale_code)
    except:
        try:
            return Locale.parse(locale_code, sep='-')
        except:
            return None

def lang(locale_code):
    l = get_locale(locale_code)
    return l.language if l else None

def region(locale_code):
    l = get_locale(locale_code)
    return l.territory if l else None

def script(locale_code):
    l = get_locale(locale_code)
    return l.script if l else None

def is_equal_lang(locale1, locale2):
    l1, l2 = lang(locale1), lang(locale2)
    return (l1 and l2) and l1==l2

def is_equal_script(locale1, locale2):
    s1, s2 = script(locale1), script(locale2)
    return (s1 and s2) and s1==s2

def is_equal_lang_and_script(locale1, locale2):
    return is_equal_lang(locale1, locale2) and is_equal_script(locale1,locale2)
