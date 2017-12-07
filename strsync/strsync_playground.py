# -*- coding: utf-8 -*-

import googletrans
from googletrans import Translator
from googletrans.constants import DEFAULT_USER_AGENT, LANGCODES, LANGUAGES, SPECIAL_CASES
translator = Translator()

print googletrans.LANGCODES
print googletrans.constants
print [l.text for l in translator.translate(['hi','you'], src='en', dest='ko')]
