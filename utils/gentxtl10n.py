#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, fnmatch, re, codecs, argparse
from os.path import expanduser
from google.cloud import translate


def supported_locale_codes():
    return [l[u'language'] for l in translate.Client().get_languages()]


def get_translating_locale_code(forcode):
    code_map = {
        'zh-Hans': 'zh',
        'zh-Hant': 'zh-TW'
    }
    return code_map[forcode] if forcode in code_map else forcode


parser = argparse.ArgumentParser(
    description='Extract elements from from Swift code to the .strings file.')

parser.add_argument(
    'src_paths',
    help=
    'A dir path where user-created txt file located in, default="./" (e.g.: ./usersl10ntxtfiles/ ))',
    default='./',
    type=str,
    nargs='?')
parser.add_argument(
    'dest_lang_paths_as_code',
    help=
    'language codes (each localizing dir name) to translate',
    default='ja ko zh-Hans zh-Hant',
    type=str,
    nargs='?')

args = vars(parser.parse_args())

src_paths = [expanduser(path) for path in args['src_paths'].split(" ")]
loc_codes = args['dest_lang_paths_as_code'].split(" ")
supported_langs = supported_locale_codes()

for src_path in src_paths:
    host_filename = os.path.basename(src_path)
    host_dir = os.path.dirname(os.path.dirname(src_path))
    src_text_lines = codecs.open(src_path, "r", "utf-8").readlines()

    for l in loc_codes:
        dest_l = get_translating_locale_code(l)
        dest_dir_path = os.path.join(host_dir, l)
        dest_file_path = os.path.join(dest_dir_path, host_filename)
        if not os.path.exists(dest_dir_path):
            os.mkdir(dest_dir_path)

        print("Translating ...", l, ">", dest_l, dest_file_path)
        dest_text_lines = [t[u'translatedText'] + '\n' for t in
                           translate.Client(target_language=dest_l).translate(src_text_lines)]
        wcur = codecs.open(dest_file_path, "w", "utf-8")
        wcur.writelines(dest_text_lines)
        wcur.close()
