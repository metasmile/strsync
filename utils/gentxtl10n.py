#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os, fnmatch, re, codecs, argparse, shutil, errno
from os.path import expanduser
from google.cloud import translate

__QUOTES_RE__ = re.compile(r"\"")
__QUOTES_REPLACEMENT__ = "'"

__encoded_apostrophe_RE__ = re.compile(r"&#39;") #  regex: "&#[0-9]{1,};"
__encoded_apostrophe_REPLACEMENT__ = "'"

def proc_after_translate(_str):
    _str = __QUOTES_RE__.sub(__QUOTES_REPLACEMENT__, _str)
    # remove Encoded Quotes
    _str = __encoded_apostrophe_RE__.sub(__encoded_apostrophe_REPLACEMENT__, _str)
    return _str

def copydir(source, dest, exclude_if_existed=[]):
    """Copy a directory structure overwriting existing files"""
    for root, dirs, files in os.walk(source):
        if not os.path.isdir(root):
            os.makedirs(root)
        for each_file in files:
            rel_path = root.replace(source, '').lstrip(os.sep)
            dest_dir = os.path.join(dest, rel_path)
            dest_path = os.path.join(dest, rel_path, each_file)
            src_path = os.path.join(root, each_file)

            if not os.path.exists(dest_dir):
                os.mkdir(dest_dir)

            if len(exclude_if_existed) and os.path.exists(dest_path) and os.path.basename(dest_path) in exclude_if_existed:
                continue

            shutil.copy2(src_path, dest_path)

def supported_locale_codes():
    return [l[u'language'] for l in translate.Client().get_languages()]

#https://github.com/fastlane/fastlane/blob/master/fastlane_core/lib/fastlane_core/languages.rb
def get_translating_locale_code(forcode):
    code_map = {
        'zh-Hans' : 'zh',
        'zh-Hant': 'zh-TW'
    }
    return code_map[forcode] if forcode in code_map else forcode

parser = argparse.ArgumentParser(
    description='Extract elements from from Swift code to the .strings file.')

parser.add_argument(
    'src_paths',
    help=
    'A dir path where user-created txt file located in, default="./" (e.g.: ./usersl10n/ ))',
    default='./',
    type=str,
    nargs='?')
parser.add_argument(
    'dest_lang_paths_as_code',
    help=
    'language codes (each localizing dir name) to translate',
    default='ja ko zh-Hans zh-Hant fr-FR de-DE es-ES es-MX pt-PT pt-BR vi',
    # python ./txtl10n.py "./fastlane/com.stells.batch/en-US/description.txt" "fr-FR de-DE es-ES es-MX pt-PT pt-BR vi"
    type=str,
    nargs='?')
parser.add_argument(
    'file_names_should_skip_if_existed',
    help=
    'file_names_should_skip_if_existed',
    default='name.txt subtitle.txt description.txt keywords.txt',
    # python ./txtl10n.py "./fastlane/com.stells.batch/en-US/description.txt" "fr-FR de-DE es-ES es-MX pt-PT pt-BR vi"
    type=str,
    nargs='?')

args = vars(parser.parse_args())

src_paths = [expanduser(path) for path in args['src_paths'].split(" ")]
loc_codes = args['dest_lang_paths_as_code'].split(" ")
ex_file_names = args['file_names_should_skip_if_existed'].split(" ")
supported_langs = supported_locale_codes()

dest_lines_by_file_path = {}

for src_path in src_paths:
    host_filename = os.path.basename(src_path)
    base_dir = os.path.dirname(src_path)
    host_dir = os.path.dirname(base_dir)
    src_text_lines = codecs.open(src_path, "r", "utf-8").readlines()

    for l in loc_codes:
        dest_l = get_translating_locale_code(l)
        dest_dir_path = os.path.join(host_dir, l)
        dest_file_path = os.path.join(dest_dir_path, host_filename)

        copydir(base_dir, dest_dir_path, ex_file_names)

        print "Translating ...", l, ">", dest_l, dest_file_path

        def _translate(dest_l, src_text_lines):
            lines = [t[u'translatedText']+'\n' for t in translate.Client(target_language=dest_l).translate(src_text_lines)]
            return map(lambda line: proc_after_translate(line), lines)

        dest_text_lines = None
        try:
            dest_text_lines = _translate(dest_l, src_text_lines)
        except Exception as err:
            #almost locale codes Google api allows are only supporting language code like 'fr'. not regional code 'fr-FR'.
            if "Invalid Value" in str(err):
                dest_text_lines = _translate(dest_l.split('-')[0], src_text_lines)

        if dest_text_lines:
            dest_lines_by_file_path[dest_file_path] = dest_text_lines

#finalize, start to write
for dest_file_path in dest_lines_by_file_path:
    wcur = codecs.open(dest_file_path, "w", "utf-8")
    wcur.writelines(dest_lines_by_file_path[dest_file_path])
    wcur.close()
