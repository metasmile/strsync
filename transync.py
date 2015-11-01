
# transync - Automatically translate and synchronize .strings files from defined base language.
# Copyright (c) 2015 Xoropsax cyrano905@gmail.com (github.com/metasmile)

from microsofttranslator import Translator
import localizable
import time, os, sys, re, textwrap, argparse, pprint, subprocess, codecs, csv
from os.path import expanduser

parser = argparse.ArgumentParser(description='Automatically translate and synchronize .strings files from defined base language.')
parser.add_argument('-b','--base-lang-name', help='A base(or source) localizable resource name.(default=\'Base\'), (e.g. "Base" via \'Base.lproj\', "en" via \'en.lproj\')', default='Base', required=False)
parser.add_argument('-x','--excluding-lang-names',type=str, help='A localizable resource name that you want to exclude. (e.g. "Base" via \'Base.lproj\', "en" via \'en.lproj\')', required=False, nargs='+')
parser.add_argument('-c','--client-id', help='Client ID for MS Translation API', required=True)
parser.add_argument('-s','--client-secret', help='Client Secret key for MS Translation API', required=True)
parser.add_argument('target path', help='Target localizable resource path. (root path of Base.lproj, default=./)', default='.', nargs='?')
args = vars(parser.parse_args())

reload(sys)
sys.setdefaultencoding('utf-8')

# configure arguments
__DIR_SUFFIX__ = ".lproj"
__FILE_SUFFIX__ = ".strings"
__RESOURCE_PATH__ = expanduser(args['target path'])
__BASE_LANG__ = args['base_lang_name']
__EXCLUDING_LANGS__ = args['excluding_lang_names']
__BASE_RESOUCE_DIR__ = None
if __BASE_LANG__.endswith(__DIR_SUFFIX__):
    __BASE_RESOUCE_DIR__ = __BASE_LANG__
    __BASE_LANG__ = __BASE_LANG__.split(__DIR_SUFFIX__)[0]
else:
    __BASE_RESOUCE_DIR__ = __BASE_LANG__+__DIR_SUFFIX__


# setup Translator & langs

# read ios langs
print '[i] fetch supported locale codes for ios9 ...'
__IOS9_CODES__ = [lang_row[0] for lang_row in csv.reader(open('./lc_ios9.tsv','rb'), delimiter='\t')]
print '[i] complete. Supported numbers of locale code :', len(__IOS9_CODES__)

__MS_CODE_ALIASES__ = {
    # MS : ISO639
    'zh-CHS' : ['zh-Hans', 'zh-CN', 'zh-SG'],
    'zh-CHT' : ['zh-Hant', 'zh-MO', 'zh-HK', 'zh-TW']
}

# read mst langs
print '[i] fetch supported locales from Microsoft Translation API...'
trans = Translator(args['client_id'], args['client_secret'])

__MS_LANG_FILE__ = './lc_ms.cached.tsv'
__MS_SUPPORTED_CODES__ = None
if os.path.exists(__MS_LANG_FILE__):
    __MS_SUPPORTED_CODES__ = [l.strip() for l in open(__MS_LANG_FILE__,'rb').readlines()]
else:
    __MS_SUPPORTED_CODES__ = trans.get_languages()
    cfile = open(__MS_LANG_FILE__,'w')
    codes = ''
    for code in __MS_SUPPORTED_CODES__:
        codes += code+'\n'
    cfile.write(codes)
    cfile.close()
print '[i] complete. Supported numbers of locale code :', len(__MS_SUPPORTED_CODES__)

def strings_obj_from_file(file):
    return localizable.parse_strings(filename=file)

base_dict = None
translated_dict = {}

# Get Base Language Specs
walked = list(os.walk(expanduser(__RESOURCE_PATH__), topdown=True))

for dir, subdirs, files in walked:
    if os.path.basename(dir)==__BASE_RESOUCE_DIR__:
        base_dict = {}
        for _file in files:
            base_dict[_file] = strings_obj_from_file(os.path.join(dir, _file))

if not base_dict:
    print '[!] Not found "{0}" in target path "{1}"'.format(__BASE_RESOUCE_DIR__, __RESOURCE_PATH__)
    sys.exit(0)

for dir, subdirs, files in walked:
    if dir.endswith((__DIR_SUFFIX__)):
        lc = os.path.basename(dir).split(__DIR_SUFFIX__)[0]
        if lc.find('_'): lc = lc.replace('_','-')

        if lc in __EXCLUDING_LANGS__:
            continue

        files = map(lambda f: f.decode('utf-8'), filter(lambda f: f.endswith(__FILE_SUFFIX__), files))

        added_files = list(set(base_dict.keys()) - set(files))
        removed_files = list(set(files) - set(base_dict.keys()))
        existing_file = list(set(files) - set(added_files) - set(removed_files))

        # print "Added:", added_files, "Removed:", removed_files, "Existing:", existing_file

        #remove - file
        for removed_file in removed_files:
            # print removed_file
            os.rename(os.path.join(dir, removed_file), os.path.join(dir, removed_file+'.deleted'))

        #update - file
        for ext_file in existing_file:
            base_content = base_dict[ext_file]
            base_keys = [key['key'] for key in base_content]

            target_content = localizable.parse_strings(filename=os.path.join(dir, ext_file))
            target_keys = [key['key'] for key in target_content]

            adding_keys = list(set(base_keys) - set(target_keys))
            removing_keys = list(set(target_keys) - set(base_keys))
            existing_keys = list(set(base_keys) - set(adding_keys) - set(removing_keys))

            for k in adding_keys:
                i = base_keys.index(k)
                o = base_content[i]
                if i<len(target_content):
                    target_content.insert(i, o)
                else:
                    target_content.append(o)

                print base_content[i]

            # print lc, adding_keys, removing_keys

        #add - file
        for added_file in added_files:
            base = base_dict[added_file]
            # print os.path.join(dir, added_file)


# strings = localizable.parse_strings(filename='ar.lproj/Localizable.strings')
# values = ''
# for k in strings:
#     values += "\"{0}\" = \"{1}\";\n".format(k['key'], k['value'])

# path = os.path.join(expanduser('./'), 'ar.lproj/Localizable.strings')
# f = codecs.open(path, "w", "utf-8")
# f.write(values)
# f.close()
