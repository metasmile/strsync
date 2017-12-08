# -*- coding: utf-8 -*-

import googletrans
from googletrans import Translator
from googletrans.constants import DEFAULT_USER_AGENT, LANGCODES, LANGUAGES, SPECIAL_CASES
translator = Translator()

# print googletrans.LANGCODES
# print googletrans.constants
# print [l.text for l in translator.translate(['hi','you'], src='en', dest='ko')]

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
