
# transync - Automatically translate and synchronize .strings files from defined base language.
# Copyright (c) 2015 Xoropsax cyrano905@gmail.com (github.com/metasmile)

import localizable
import time, os, sys, re, textwrap, argparse, pprint, subprocess, codecs
from os.path import expanduser

parser = argparse.ArgumentParser(description='Automatically translate and synchronize .strings files from defined base language.')
parser.add_argument('target path', help='Target localizable resource path. (root path of Base.lproj, default=./)', default='.', nargs='?')
args = vars(parser.parse_args())

reload(sys)
sys.setdefaultencoding('utf-8')

__RESOURCE_PATH__ = expanduser(args['target path'])
__BASE_LANG__ = "Base"
__DIR_SUFFIX__ = ".lproj"

# Base.lproj key value

def strings_obj_from_file(file):
    return localizable.parse_strings(filename=file)

base_dict = {}
translated_dict = {}

# Get Base Language Specs
walked = list(os.walk(expanduser(__RESOURCE_PATH__), topdown=True))

for dir, subdirs, files in walked:
    if os.path.basename(dir)==__BASE_LANG__+__DIR_SUFFIX__:
        for _file in files:
            base_dict[_file] = strings_obj_from_file(os.path.join(dir, _file))

for dir, subdirs, files in walked:
    if dir.endswith((__DIR_SUFFIX__)):
        added_files = list(set(base_dict.keys()) - set(files))
        removed_files = list(set(files) - set(base_dict.keys()))
        existing_file = list(set(files) - set(added_files))

        print "Added:", added_files, "Removed:", removed_files

        #remove
        for removed_file in removed_files:
            os.rename(removed_file, removed_file+'.deleted')

        #update
        for ext_file in existing_file:
            base_content = base_dict[ext_file]
            base_keys = [key['key'] for key in base_content]

            target_content = localizable.parse_strings(filename=os.path.join(dir, ext_file))
            target_keys = [key['key'] for key in target_content]

            added_keys = list(set(base_keys) - set(target_keys))
            removed_keys = list(set(target_keys) - set(base_keys))

            print added_keys, removed_keys

        #add
        for added_file in added_files:
            base = base_dict[added_file]
            print os.path.join(dir, added_file)

# strings = localizable.parse_strings(filename='ar.lproj/Localizable.strings')
# values = ''
# for k in strings:
#     values += "\"{0}\" = \"{1}\";\n".format(k['key'], k['value'])

# path = os.path.join(expanduser('./'), 'ar.lproj/Localizable.strings')
# f = codecs.open(path, "w", "utf-8")
# f.write(values)
# f.close()

# import goslate
# gs = goslate.Goslate()
# print gs.translate('hello world', 'de')
