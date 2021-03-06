# -*- coding: utf-8 -*-

from pytest import raises
import sys, re

from strsync.strsync import *

def test_literal_replacement():
    lines='''\
    Worker name is %s and id is %d
    That is %i%%
    %c
    Decimal: %d  Justified: %.6d
    %10c%5hc%5C%5lc
    The temp is %.*f
    %ss%lii
    ${replacement}
    %*.*s | %.3d | %lC | %s%%%02d'''

    cfmt = strtrans.__LITERAL_REGEX__

    for line in lines.splitlines():
        print '"{}"\n\t{}\n'.format(line, tuple((m.start(1), m.group(1)) for m in re.finditer(cfmt, line, flags=re.X)))

    tokens = []
    token = []
    tokenized_index = 0
    target_str = "Edit %d %@ add %f %f photo(s)"

    for m in re.finditer(cfmt, target_str, flags=re.X):
        token.append(target_str[tokenized_index:m.start(1)])
        tokens.append({
            "index" : m.start(1),
            "length" : len(m.group(1)),
            "text" : m.group(1)
        })
        tokenized_index = m.start(1)+len(m.group(1))

        target_str = target_str.replace(m.group(1),"**")
        print m.start(1), m.group(1)

    print target_str,token,tokens
    assert re.sub(re.compile(cfmt), "**", target_str) == "Edit ** ** add ** ** photo(s)"

def test_locales():
    aliases = {
        'zh-cn': 'zh-Hans',
        'zh-CN': 'zh-Hans',
        'zh-HK': 'zh-Hant',
        'zh-TW': 'zh-Hant',
        'zh-SG': 'zh-Hans'
    }

    for k in aliases:
        assert strlocale.is_equal_lang_and_script(k,aliases[k])

    # #play matched locale
    support_by_google = ['de', 'be', 'gl', 'mk', 'ur', 'pl', 'st', 'sw', 'is', 'tr', 'ro', 'so', 'hmn', 'id', 'km', 'hu', 'ca', 'ky', 'fi', 'su', 'sr', 'it', 'pt', 'cs', 'eu', 'ja', 'am', 'fa', 'tg', 'yi', 'xh', 'et', 'te', 'mr', 'sn', 'ps', 'gu', 'nl', 'mg', 'la', 'ig', 'yo', 'fr', 'hy', 'af', 'tl', 'uz', 'sq', 'vi', 'lv', 'jw', 'hr', 'gd', 'sk', 'es', 'eo', 'co', 'hi', 'da', 'bg', 'mi', 'haw', 'bs', 'ka', 'ms', 'lb', 'ht', 'ny', 'bn', 'ru', 'th', 'ta', 'ceb', 'zh-tw', 'ml', 'ha', 'ga', 'ku', 'kn', 'mn', 'iw', 'ar', 'si', 'sv', 'zu', 'sm', 'sl', 'az', 'sd', 'ko', 'lo', 'my', 'uk', 'cy', 'lt', 'no', 'mt', 'kk', 'ne', 'pa', 'el', 'en', 'zh-cn', 'fy']
    __DEFAULT_XCODE_LPROJ_NAMES__ = ['el','fr_CA','vi','ca','it','zh_HK','ar','cs','id','es','en-GB','ru','nl','pt','no','tr','en-AU','th','ro','pl','fr','uk','hr','de','hu','hi','fi','da','ja','he','pt_PT','zh_TW','sv','es_MX','sk','zh_CN','ms']

    assert strlocale.matched_locale_code('de-DE',support_by_google)
    assert strlocale.matched_locale_code('de',support_by_google)
    assert strlocale.matched_locale_code('de_DE',support_by_google)
    assert strlocale.matched_locale_code('zh_HK',support_by_google)
    assert strlocale.matched_locale_code('zh-HK',support_by_google)
    assert strlocale.matched_locale_code('fr',support_by_google)
    assert strlocale.matched_locale_code('zh_hans',support_by_google)
    assert strlocale.matched_locale_code('zh-hant',support_by_google)
    assert strlocale.matched_locale_code('zh-Hans_HK',support_by_google)
    assert strlocale.matched_locale_code('fr_CA',__DEFAULT_XCODE_LPROJ_NAMES__)
    assert strlocale.matched_locale_code('en_GB',__DEFAULT_XCODE_LPROJ_NAMES__)
    assert strlocale.matched_locale_code('en_AU',__DEFAULT_XCODE_LPROJ_NAMES__)
    assert strlocale.matched_locale_code('en-AU',__DEFAULT_XCODE_LPROJ_NAMES__)
    assert strlocale.matched_locale_code('fr_CA',support_by_google)
    assert strlocale.matched_locale_code('en_GB',support_by_google)
    assert strlocale.matched_locale_code('en_AU',support_by_google)
    assert strlocale.matched_locale_code('en-AU',support_by_google)
    assert strlocale.matched_locale_code('zh_CN',support_by_google)
    assert strlocale.matched_locale_code('zh-CN',support_by_google)
    assert strlocale.matched_locale_code('zh_CN',__DEFAULT_XCODE_LPROJ_NAMES__)
    assert strlocale.matched_locale_code('zh-CN',__DEFAULT_XCODE_LPROJ_NAMES__)
    assert strlocale.matched_locale_code('zh-AA_CC',support_by_google)
    assert strlocale.matched_locale_code('zh_BB-CC',support_by_google)
    assert strlocale.matched_locale_code('tl_CC',support_by_google)
    assert strlocale.matched_locale_code('zh-AA_CC',__DEFAULT_XCODE_LPROJ_NAMES__)
    assert strlocale.matched_locale_code('zh_BB-CC',__DEFAULT_XCODE_LPROJ_NAMES__)
    assert strlocale.matched_locale_code('es_MX',__DEFAULT_XCODE_LPROJ_NAMES__)
    assert strlocale.matched_locale_code('es-MX',__DEFAULT_XCODE_LPROJ_NAMES__)
    assert strlocale.matched_locale_code('es_MX',support_by_google)
    assert strlocale.matched_locale_code('es-MX',support_by_google)
    assert strlocale.matched_locale_code('he',__DEFAULT_XCODE_LPROJ_NAMES__)
    assert strlocale.matched_locale_code('iw',__DEFAULT_XCODE_LPROJ_NAMES__)
    assert strlocale.matched_locale_code('he',support_by_google)
    assert strlocale.matched_locale_code('iw',support_by_google)
    #
    #intersaction code
    # inter_xcode_for_google = strlocale.intersacted_locale_codes(__DEFAULT_XCODE_LPROJ_NAMES__, support_by_google)
    # assert len(set(inter_xcode_for_google)-set(support_by_google))==0
    #
    # inter_google_for_xcode = strlocale.intersacted_locale_codes(support_by_google, __DEFAULT_XCODE_LPROJ_NAMES__)
    # assert len(set(inter_google_for_xcode)-set(__DEFAULT_XCODE_LPROJ_NAMES__))==0
    #
    # #mapped codes
    # mapped_xcode_for_google = strlocale.map_locale_codes(__DEFAULT_XCODE_LPROJ_NAMES__,support_by_google)
    # print mapped_xcode_for_google
    #
    # mapped_google_for_xcode = strlocale.map_locale_codes(support_by_google, __DEFAULT_XCODE_LPROJ_NAMES__)
    # print mapped_google_for_xcode

