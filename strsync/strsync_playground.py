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
