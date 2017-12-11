# -*- coding: utf-8 -*-

#play translator

import googletrans
from googletrans import Translator
from googletrans.constants import DEFAULT_USER_AGENT, LANGCODES, LANGUAGES, SPECIAL_CASES
translator = Translator()

# print googletrans.LANGCODES
# print googletrans.constants
# print [l.text for l in translator.translate(['hi','you'], src='en', dest='ko')]


#play locale alias
import strlocale

test_l1 = 'zh-cn'
test_l2 = 'zh-tw'

for l in ['zh-Hans', 'zh-CN', 'zh-SG'] + ['zh-Hant', 'zh-MO', 'zh-HK', 'zh-TW']:
    print strlocale.lang(l)
    print strlocale.region(l)
    print strlocale.script(l)
    print strlocale.is_equal_lang_and_script(test_l1,l)
    print strlocale.is_equal_lang_and_script(test_l2,l)
    print '---'

#play format literal
import re

lines='''\
Worker name is %s and id is %d
That is %i%%
%c
Decimal: %d  Justified: %.6d
%10c%5hc%5C%5lc
The temp is %.*f
%ss%lii
%*.*s | %.3d | %lC | %s%%%02d'''

cfmt='''\
(                                  # start of capture group 1
%                                  # literal "%"
(?:                                # first option
(?:[-+0 #]{0,5})                   # optional flags
(?:\d+|\*)?                        # width
(?:\.(?:\d+|\*))?                  # precision
(?:h|l|ll|w|I|I32|I64)?            # size
[cCdiouxXeEfgGaAnpsSZ]             # type
) |                                # OR
%%)                                # literal "%%"
'''

for line in lines.splitlines():
    print '"{}"\n\t{}\n'.format(line,
           tuple((m.start(1), m.group(1)) for m in re.finditer(cfmt, line, flags=re.X)))



#play matched locale
support_by_google = ['de', 'be', 'gl', 'mk', 'ur', 'pl', 'st', 'sw', 'is', 'tr', 'ro', 'so', 'hmn', 'id', 'km', 'hu', 'ca', 'ky', 'fi', 'su', 'sr', 'it', 'pt', 'cs', 'eu', 'ja', 'am', 'fa', 'tg', 'yi', 'xh', 'et', 'te', 'mr', 'sn', 'ps', 'gu', 'nl', 'mg', 'la', 'ig', 'yo', 'fr', 'hy', 'af', 'tl', 'uz', 'sq', 'vi', 'lv', 'jw', 'hr', 'gd', 'sk', 'es', 'eo', 'co', 'hi', 'da', 'bg', 'mi', 'haw', 'bs', 'ka', 'ms', 'lb', 'ht', 'ny', 'bn', 'ru', 'th', 'ta', 'ceb', 'zh-tw', 'ml', 'ha', 'ga', 'ku', 'kn', 'mn', 'iw', 'ar', 'si', 'sv', 'zu', 'sm', 'sl', 'az', 'sd', 'ko', 'lo', 'my', 'uk', 'cy', 'lt', 'no', 'mt', 'kk', 'ne', 'pa', 'el', 'en', 'zh-cn', 'fy']
__DEFAULT_XCODE_LPROJ_NAMES__ = ['el','fr_CA','vi','ca','it','zh_HK','ar','cs','id','es','en-GB','ru','nl','pt','no','tr','en-AU','th','ro','pl','fr','uk','hr','de','hu','hi','fi','da','ja','he','pt_PT','zh_TW','sv','es_MX','sk','zh_CN','ms']

# print strlocale.matched_locale_code('de',support_by_google)
print strlocale.matched_locale_code('de-DE',support_by_google)
print strlocale.matched_locale_code('zh_HK',support_by_google)
print strlocale.matched_locale_code('zh-HK',support_by_google)
print strlocale.matched_locale_code('fr',support_by_google)
print strlocale.matched_locale_code('zh_hans',support_by_google)
print strlocale.matched_locale_code('zh-hant',support_by_google)
print strlocale.matched_locale_code('zh-Hans_HK',support_by_google)
print
print strlocale.matched_locale_code('fr_CA',__DEFAULT_XCODE_LPROJ_NAMES__)
print strlocale.matched_locale_code('en_GB',__DEFAULT_XCODE_LPROJ_NAMES__)
print strlocale.matched_locale_code('en_AU',__DEFAULT_XCODE_LPROJ_NAMES__)
print
print strlocale.matched_locale_code('fr_CA',support_by_google)
print strlocale.matched_locale_code('en_GB',support_by_google)
print strlocale.matched_locale_code('en_AU',support_by_google)
print
print strlocale.matched_locale_code('zh_CN',support_by_google)
print strlocale.matched_locale_code('zh-CN',support_by_google)
print
print strlocale.matched_locale_code('zh_CN',__DEFAULT_XCODE_LPROJ_NAMES__)
print strlocale.matched_locale_code('zh-CN',__DEFAULT_XCODE_LPROJ_NAMES__)
print
print strlocale.matched_locale_code('zh-AA_CC',support_by_google)
print strlocale.matched_locale_code('zh_BB-CC',support_by_google)
print strlocale.matched_locale_code('tl_CC',support_by_google)
print
print strlocale.matched_locale_code('zh-AA_CC',__DEFAULT_XCODE_LPROJ_NAMES__)
print strlocale.matched_locale_code('zh_BB-CC',__DEFAULT_XCODE_LPROJ_NAMES__)

#intersaction code
inter_xcode_for_google = strlocale.intersacted_locale_codes(__DEFAULT_XCODE_LPROJ_NAMES__, support_by_google)
print inter_xcode_for_google
assert len(set(inter_xcode_for_google)-set(support_by_google))==0

inter_google_for_xcode = strlocale.intersacted_locale_codes(support_by_google, __DEFAULT_XCODE_LPROJ_NAMES__)
print inter_google_for_xcode
assert len(set(inter_google_for_xcode)-set(__DEFAULT_XCODE_LPROJ_NAMES__))==0
