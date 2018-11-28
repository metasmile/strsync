# -*- coding: utf-8 -*-
from babel import Locale, UnknownLocaleError

__LOCALE_SEP_SCRIPT__ = '-'
__LOCALE_SEP_REGION__ = '_'

_cached_locale_ = {}


def get_locale(locale_code):
    locale = None

    try:
        locale = Locale.parse(locale_code)
    except (UnknownLocaleError, ValueError) as e:
        try:
            locale = Locale.parse(locale_code, sep='-')
        except (UnknownLocaleError, ValueError) as e:
            pass

    if locale_code in _cached_locale_:
        locale = _cached_locale_[locale_code]

    if locale:
        _cached_locale_[locale_code] = locale

    return locale


def lang(locale_code):
    l = get_locale(locale_code)
    return l.language if l else None


def is_equal_lang(locale1, locale2):
    l1, l2 = lang(locale1), lang(locale2)
    return (l1 and l2) and l1 == l2


def region(locale_code):
    l = get_locale(locale_code)
    return l.territory if l else None


def is_equal_region(locale1, locale2):
    r1, r2 = region(locale1), region(locale2)
    return (r1 and r2) and r1 == r2


def script(locale_code):
    l = get_locale(locale_code)
    return l.script if l else None


def is_equal_script(locale1, locale2):
    s1, s2 = script(locale1), script(locale2)
    return (s1 and s2) and s1 == s2


def is_equal_lang_and_script(locale1, locale2):
    return is_equal_lang(locale1, locale2) and is_equal_script(locale1, locale2)


def matched_locale_code(code, for_codes):

    if code in for_codes:
        return code
    else:
        lang_matched_codes = filter(lambda l: is_equal_lang(code, l), for_codes)

        # fallback by only lang code
        if not lang_matched_codes:
            if __LOCALE_SEP_SCRIPT__ in code:
                return matched_locale_code(code.split(__LOCALE_SEP_SCRIPT__)[0], for_codes)
            elif __LOCALE_SEP_REGION__ in code:
                return matched_locale_code(code.split(__LOCALE_SEP_REGION__)[0], for_codes)
        # found unique one
        elif len(lang_matched_codes) == 1:
            return lang_matched_codes[0]
        # found several aliases
        elif len(lang_matched_codes) > 1:
            script_matched_codes = filter(lambda l: is_equal_script(code, l), lang_matched_codes)
            region_matched_codes = filter(lambda l: is_equal_region(code, l), lang_matched_codes)

            primary_matched_codes = script_matched_codes or region_matched_codes
            intersacted_codes = list(set(script_matched_codes) & set(region_matched_codes))

            # phase 1 - intersacted
            if intersacted_codes:
                return intersacted_codes[0]
            # phase 2 - match by primary matched
            elif primary_matched_codes:
                return primary_matched_codes[0]
            # phase 3 - forcefully return with first lang
            else:
                return lang_matched_codes[0]

    return None


def intersacted_locale_codes(codes, for_codes):
    alt_matched_codes = []
    for c in list(set(codes) - set(for_codes)):
        matched_code = matched_locale_code(c, for_codes)
        if matched_code:
            alt_matched_codes.append(matched_locale_code(c, for_codes))
    return list((set(for_codes) - set(codes)) | set(alt_matched_codes))


def map_locale_codes(matching_codes, for_codes):
    mapped = {}
    for c in matching_codes:
        m = matched_locale_code(c, for_codes)
        if m:
            mapped[c] = m
    return mapped


# Language Support for the Neural Machine Translation Model: https://cloud.google.com/translate/docs/languages
def default_supporting_xcode_lang_codes():
    return [
        'ko',
        'el',
        'vi',
        'ca',
        'it',
        'zh-HK',
        'ar',
        'cs',
        'id',
        'es',
        'ru',
        'nl',
        'pt',
        'nb',
        'tr',
        'th',
        'ro',
        'pl',
        'fr',
        'uk',
        'hr',
        'de',
        'hu',
        'hi',
        'fi',
        'da',
        'ja',
        'he',
        'zh-Hans',
        'zh-Hant',
        'sv',
        'sk',
        'ms'
    ]

def secondary_supporting_xcode_lang_codes():
    return [
        'hy', 'az', 'gu', 'co', 'af', 'sw', 'is', 'am', 'eo', 'ne', 'st', 'cy', 'gd', 'km', 'ga', 'zu', 'eu',
        'et', 'xh',
        'gl', 'ig', 'ps', 'sr', 'lb', 'lo', 'tl', 'lv', 'ny', 'lt', 'pa', 'tg', 'te', 'ta', 'yi', 'bg', 'sm', 'yo',
        'sl', 'fy', 'bn', 'jw', 'ka', 'ht', 'fa', 'bs', 'ha', 'mg', 'uz', 'kk', 'ml', 'sq', 'mn', 'mi', 'kn', 'mk',
        'ur', 'mt', 'si', 'so', 'sn', 'ku', 'mr', 'sd'
    ]
