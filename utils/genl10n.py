#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os, time, datetime, re, argparse, textwrap, subprocess
from datetime import date, timedelta
from time import mktime
from os.path import expanduser
import shutil
from distutils.dir_util import copy_tree
import json
import glob
import codecs
import fnmatch
import collections

parser = argparse.ArgumentParser(
    description='Extract elements from from Swift code to the .strings file.')

parser.add_argument('src_paths', help='Main swift source path, default="./")',
                    default='./', type=str, nargs='?')
parser.add_argument('dest_l10n_base_path', help='Target Base Localizable.strings path. (default=./)',
                    default='./', nargs='?')
parser.add_argument('-k', '--split-key',
                    help='Splitting identifier to extract strings from Swift code. (e.g. "This is string".localized )',
                    default='.localized', required=False)
args = vars(parser.parse_args())

src_paths = [expanduser(path) for path in args['src_paths'].split(" ")]

dest_l10n_base_path = expanduser(args['dest_l10n_base_path'])
split_key = args['split_key']

__GEN_FLAG__ = "Generated from genl10n"

complied_patterns_by_priority = [
    re.compile(r'((\"\b.*\b\")' + split_key + ')', re.I|re.U|re.MULTILINE|re.X)
    , re.compile(r'((\".*\")' + split_key + ')', re.I|re.U|re.MULTILINE|re.X)
]

# for excluing format literal -> \(value)
qs = re.compile(r'\\\((.+)\)', re.I|re.U)
# for excluing code comment
cs = re.compile(r'\/\/.*', re.I|re.U)

swift_files = []

for src_path in src_paths:
    for root, dirnames, filenames in os.walk(src_path):
        for filename in fnmatch.filter(filenames, '*.swift'):
            swift_files.append(os.path.join(root, filename))

gened_strs = collections.OrderedDict()
for code_file in swift_files:
    rcur = codecs.open(code_file, "r", "utf-8")
    wlines = []
    for i, line in enumerate(rcur.readlines()):

        if cs.search(line):
            line = cs.sub("", line)

        for line_sp in line.split(split_key):

            for p in complied_patterns_by_priority:
                loc_strs = p.search(line_sp + split_key)

                if loc_strs:
                    str = loc_strs.group()

                    #TODO: fix for a case "Videos from \"Screen Recording\""

                    # unwrap overlapped quote "
                    str = '"'+str.split('"')[-2]+'"'

                    if qs.search(str):
                        # for excluding literal format e.g. -> %d \(pluralizedString)
                        continue

                    if not str in gened_strs:
                        gened_strs[str] = set()

                    gened_strs[str].add((code_file, i+1))
                    break # if pattern was found by one of them, exit loop

rcur = codecs.open(dest_l10n_base_path, "r", "utf-8")
rlines = rcur.readlines()
rcur.close()

wlines = []
met_gen_flag = False
for line in rlines:
    if __GEN_FLAG__ in line:
        met_gen_flag = True
        continue

    if met_gen_flag:
        met_gen_flag = False
        continue

    wlines.append(line)


keys_in_l10n_file = map(lambda line: line.split("=")[0].strip(), wlines)
keys_in_gened_strs = sorted(gened_strs.keys())#[k for k, v in sorted(gened_strs.items())]
#FIXME: python2.7 <-> 3 dict key ordering is fucking different  what??

if keys_in_gened_strs and len(wlines[-1].strip()) > 0:
    wlines.append('\n')

for new_key in keys_in_gened_strs:
    if new_key in keys_in_l10n_file:
        continue

    new_line = u'{0} = {0};'.format(new_key)

    # gened_strs[new_key][0] : code file path as string
    # gened_strs[new_key][1] : line as int

    # from_files = ", ".join(map(lambda s: "{}#{}".format(os.path.basename(s[0]), s[1]), gened_strs[new_key]))
    from_files = ", ".join(map(lambda s: "{}".format(os.path.basename(s[0])), gened_strs[new_key]))
    wlines.append("/* {}: {} */".format(__GEN_FLAG__, from_files))
    wlines.append('\n')
    wlines.append(new_line)
    wlines.append('\n')

wcur = codecs.open(dest_l10n_base_path, "w", "utf-8")
wcur.writelines(wlines)
wcur.close()
