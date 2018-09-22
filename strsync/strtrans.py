from google.cloud import translate

# Install: https://cloud.google.com/translate/docs/reference/libraries#client-libraries-install-python
# Docs: https://googlecloudplatform.github.io/google-cloud-python/latest/translate/usage.html
import strlocale
import re

# https://developer.apple.com/library/content/documentation/Cocoa/Conceptual/Strings/Articles/formatSpecifiers.html
__LITERAL_REGEX__ = '''\
    (                                  # start of capture group 1
    %                                  # literal "%"
    (?:                                # first option
    (?:[-+0 #]{0,5})                   # optional flags
    (?:\d+|\*)?                        # width
    (?:\.(?:\d+|\*))?                  # precision
    (?:h|l|ll|w|I|I32|I64)?            # size
    [cCdiouxXeEfgGaAnpsSZ@]            # type
    )                                  # OR
    | \$\{.+\}                         # replacement for property "%{appName}"
    | %%                               # literal "%%"
    )
'''
__LITERNAL_FORMAT_RE__ = re.compile(__LITERAL_REGEX__, flags=re.X)

__LITERNAL_REPLACEMENT_RE__ = re.compile(r'\{\^{1,}\}')


def __LITERNAL_REPLACEMENT__(id):
    assert isinstance(id, int) and id >= 0, "id is must be an integer and 1 or higher"
    return "{%s}" % ("^" * (id + 1))

def __strip_emoji__(data):
    if not data:
        return data
    if not isinstance(data, basestring):
        return data
    try:
    # UCS-4
        patt = re.compile(u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])')
    except re.error:
    # UCS-2
        patt = re.compile(u'([\u2600-\u27BF])|([\uD83C][\uDF00-\uDFFF])|([\uD83D][\uDC00-\uDE4F])|([\uD83D][\uDE80-\uDEFF])')
    return patt.sub('', data)

__QUOTES_RE__ = re.compile(r"\"")
__QUOTES_REPLACEMENT__ = "'"

__MULTIPLE_SUFFIX_RE__ = re.compile(r'(.*)(\(s\))(.*)')
__MULTIPLE_SUFFIX_ALTER_REPLACEMENT__ = "s"
__MULTIPLE_SUFFIX_NOT_SUPPORTED_LANGS__ = ['zh', 'ro', 'vi']


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
        assert len(filter(lambda i: i is not None, [item.trans_output_text for item in pretrans_items])) == len(
            pretrans_items), "translation result 'trans_output_text' pretrans_items is empty."

        self.pretrans_items = pretrans_items

    def finalize_strs(self):
        assert len(self.pretrans_items), "translated_items is empty."
        return [self.__postprocess_str(titem) for titem in self.pretrans_items]

    @staticmethod
    def __postprocess_str(pretrans_item):
        # remove Quotes
        _str = __QUOTES_RE__.sub(__QUOTES_REPLACEMENT__, pretrans_item.trans_output_text.strip())
        # replace tp liternal replacement
        for i, m in enumerate(pretrans_item.matched_literal_items):
            # print m.replacement, '->', m.literal
            _str = _str.replace(m.replacement, m.literal, 1)
        return _str

def supported_locale_codes():
    return [l[u'language'] for l in translate.Client().get_languages()]

def translate_strs(strs, to):
    __trans = translate.Client(target_language=to)

    assert len(strs) or isinstance(strs[0], str), "Input variables should be string list"
    pre_items = [item for item in __preprocessing_translate_strs(strs, to)]

    translated_items = __trans.translate([item.trans_input_text for item in pre_items])
    assert len(translated_items) == len(pre_items), "the numbers of input items and translated items must be same."

    # map results
    for i, t in enumerate(translated_items):
        _result = t[u'translatedText']
        _pre_trans_item = pre_items[i]

        _literal_replacement_exist = bool(len(_pre_trans_item.matched_literal_items))
        _literal_replacement_contains_all = bool(
            len(filter(lambda s: s in _result, [mitem.replacement for mitem in _pre_trans_item.matched_literal_items])))

        # if literal replacement did not contain from translator, use original text.
        if _literal_replacement_exist and not _literal_replacement_contains_all:
            _pre_trans_item.trans_output_text = _pre_trans_item.original_text
        # else, it means all replacing processes are completed, use/commit translated text.
        else:
            _pre_trans_item.trans_output_text = _result

        # print pre_items[i].trans_input_text, '->' , pre_items[i].trans_output_text
    return __PostprocessingTransItem(pre_items).finalize_strs()

def __preprocessing_translate_strs(strs, dest_lang):
    preitems = []
    for s in strs:
        otext = s.strip()

        # process multiple suffixs
        if strlocale.lang(dest_lang) in __MULTIPLE_SUFFIX_NOT_SUPPORTED_LANGS__:
            otext = re.sub(__MULTIPLE_SUFFIX_RE__, r'\1s\3', otext)

        pretext = otext

        # remove emoji and special characters
        pretext = __strip_emoji__(pretext)

        # process literals
        found_literals = list(re.finditer(__LITERAL_REGEX__, otext, flags=re.X))
        prematched_literal_items = []

        if len(found_literals):
            literals, indexes = zip(*[(m.group(0), (m.start(), m.end() - 1)) for m in found_literals])
            for i, l in enumerate(literals):
                lr = __LITERNAL_REPLACEMENT__(i)
                pretext = pretext.replace(l, lr, 1)
                prematched_literal_items.append(
                    __PreTransMatchedLiteralItem(indexes[i], l, __LITERNAL_REPLACEMENT__(i)))

        preitems.append(__PreTransItem(otext, pretext, prematched_literal_items))
    return preitems
