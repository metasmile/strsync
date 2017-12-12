
import googletrans
from googletrans import Translator
import re

#https://developer.apple.com/library/content/documentation/Cocoa/Conceptual/Strings/Articles/formatSpecifiers.html
__LITERNAL_FORMAT__ = "%@"
__LITERAL_REGEX__='''\
    (                                  # start of capture group 1
    %                                  # literal "%"
    (?:                                # first option
    (?:[-+0 #]{0,5})                   # optional flags
    (?:\d+|\*)?                        # width
    (?:\.(?:\d+|\*))?                  # precision
    (?:h|l|ll|w|I|I32|I64)?            # size
    [cCdiouxXeEfgGaAnpsSZ@]            # type
    ) |                                # OR
    %%)                                # literal "%%"
'''
__LITERNAL_FORMAT_RE__ = re.compile(__LITERAL_REGEX__, flags=re.X)

__LITERNAL_REPLACEMENT_RE__ = re.compile(r"\{\^{1,}\}")
def __LITERNAL_REPLACEMENT__(id):
    assert isinstance(id,int) and id>=0,"id is must be an integer and 1 or higher"
    return "{%s}" % ("^" * (id+1))

__QUOTES_RE__ = re.compile(r"\"")
__QUOTES_REPLACEMENT__ = "'"


class __PreTransItem(object):
    def __init__(self, original_text, trans_input_text, matched_literal_items):
        self.original_text = original_text
        self.trans_input_text = trans_input_text
        self.trans_output_text = None
        self.matched_literal_items = matched_literal_items

class __PreTransMatchedLiteralItem(object):
    def __init__(self, index, literal, replacement):
        self.index = index
        self.literal = literal
        self.replacement = replacement

class __PostprocessingTransItem(object):
    def __init__(self, pretrans_items):
        assert len(pretrans_items), "pretrans_items is empty."
        assert len(filter(lambda i: i is not None, [item.trans_output_text for item in pretrans_items]))==len(pretrans_items), "translation result 'trans_output_text' pretrans_items is empty."

        self.pretrans_items = pretrans_items

    def finalize_strs(self):
        assert len(self.pretrans_items), "translated_items is empty."
        return [self.__postprocess_str(titem) for titem in self.pretrans_items]

    def __postprocess_str(self, pretrans_item):
        # remove Quotes
        _str = __QUOTES_RE__.sub(__QUOTES_REPLACEMENT__, pretrans_item.trans_output_text.strip())
        # replace tp liternal replacement
        for i, m in enumerate(pretrans_item.matched_literal_items):
            # print m.replacement, '->', m.literal
            _str = _str.replace(m.replacement, m.literal, 1)
        return _str

__trans = Translator()

def supported_locales():
    return [l for l in googletrans.LANGCODES.values()]

def translate(strs, to):
    assert len(strs) or isinstance(strs[0], str), "Input variables should be string list"
    pre_items = [item for item in __preprocessing_translate_strs(strs)]

    translated_items = __trans.translate([item.trans_input_text for item in pre_items], dest=to)
    assert len(translated_items)==len(pre_items), "the numbers of input items and translated items must be same."

    #map results
    for i, t in enumerate(translated_items):
        pre_items[i].trans_output_text = t.text
        # print pre_items[i].trans_input_text, '->' , pre_items[i].trans_output_text

    return __PostprocessingTransItem(pre_items).finalize_strs()

def __preprocessing_translate_strs(strs):
    preitems = []
    for s in strs:
        otext = s.strip()
        pretext = otext
        literals, indexes = zip(*[(m.group(0), (m.start(), m.end()-1)) for m in re.finditer(__LITERAL_REGEX__, otext, flags=re.X)])

        prematched_items = []
        for i, l in enumerate(literals):
            lr = __LITERNAL_REPLACEMENT__(i)
            pretext = pretext.replace(l, lr, 1)
            prematched_items.append(__PreTransMatchedLiteralItem(indexes[i], l, __LITERNAL_REPLACEMENT__(i)))
        preitems.append(__PreTransItem(otext, pretext, prematched_items))
    return preitems
