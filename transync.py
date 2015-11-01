import localizable
import time, os, sys, re, textwrap, argparse, pprint, subprocess, codecs
from os.path import expanduser

reload(sys)
sys.setdefaultencoding('utf-8')

__BASE_LANG__ = "Base"
__DIR_SUFFIX__ = ".lproj"

# Base.lproj key value

def strings_obj_from_file(file):
    return localizable.parse_strings(filename=file)

base_dict = {}
translated_dict = {}

# Get Base Language Specs
walked = list(os.walk(expanduser('./'), topdown=True))

for dir, subdirs, files in walked:
    if os.path.basename(dir)==__BASE_LANG__+__DIR_SUFFIX__:
        for _file in files:
            base_dict[_file] = strings_obj_from_file(os.path.join(dir, _file))

for dir, subdirs, files in walked:
    if dir.endswith((__DIR_SUFFIX__)):
        added_files = list(set(base_dict.keys()) - set(files))
        removed_files = list(set(files) - set(base_dict.keys()))

        print "Added:", added_files, "Removed:", removed_files

        for removed_file in removed_files:
            os.rename(removed_file, removed_file+'.deleted')

        for added_file in added_files:
            print os.path.join(dir, new_file)

strings = localizable.parse_strings(filename='ar.lproj/Localizable.strings')

values = ''
for k in strings:
    values += "\"{0}\" = \"{1}\";\n".format(k['key'], k['value'])

# path = os.path.join(expanduser('./'), 'ar.lproj/Localizable.strings')
# f = codecs.open(path, "w", "utf-8")
# f.write(values)
# f.close()

# import goslate
# gs = goslate.Goslate()
# print gs.translate('hello world', 'de')
