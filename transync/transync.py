# -*- coding: utf-8 -*-
# transync - Automatically translate and synchronize .strings files from defined base language.
# Copyright (c) 2015 metasmile cyrano905@gmail.com (github.com/metasmile)

from microsofttranslator import Translator
import localizable
import time, os, sys, re, textwrap, argparse, pprint, subprocess, codecs, csv
from os.path import expanduser

def resolve_file_path(file):
    return os.path.join(os.path.dirname(__file__), file)

def join_path_all(target_dir, target_files):
    return map(lambda f: os.path.join(target_dir, f), target_files)

def main():
    parser = argparse.ArgumentParser(description='Automatically translate and synchronize .strings files from defined base language.')
    parser.add_argument('-b','--base-lang-name', help='A base(or source) localizable resource name.(default=\'Base\'), (e.g. "Base" via \'Base.lproj\', "en" via \'en.lproj\')', default='Base', required=False)
    parser.add_argument('-x','--excluding-lang-names', type=str, help='A localizable resource name that you want to exclude. (e.g. "Base" via \'Base.lproj\', "en" via \'en.lproj\')', required=False, nargs='+')
    parser.add_argument('-c','--client-id', help='Client ID for MS Translation API', required=True)
    parser.add_argument('-s','--client-secret', help='Client Secret key for MS Translation API', required=True)
    parser.add_argument('-f','--force-translate-keys', type=str, help='Keys in the strings to update and translate by force.', required=False, nargs='+')
    parser.add_argument('target path', help='Target localizable resource path. (root path of Base.lproj, default=./)', default='.', nargs='?')
    args = vars(parser.parse_args())

    reload(sys)
    sys.setdefaultencoding('utf-8')

    # configure arguments
    __LANG_SEP__ = '-'
    __DIR_SUFFIX__ = ".lproj"
    __FILE_SUFFIX__ = ".strings"
    __RESOURCE_PATH__ = expanduser(args['target path'])
    __BASE_LANG__ = args['base_lang_name']
    __EXCLUDING_LANGS__ = args['excluding_lang_names'] or []
    __FORCE_TRANSLATE__ = args['force_translate_keys'] or []
    __BASE_RESOUCE_DIR__ = None
    if __BASE_LANG__.endswith(__DIR_SUFFIX__):
        __BASE_RESOUCE_DIR__ = __BASE_LANG__
        __BASE_LANG__ = __BASE_LANG__.split(__DIR_SUFFIX__)[0]
    else:
        __BASE_RESOUCE_DIR__ = __BASE_LANG__+__DIR_SUFFIX__

    # setup Translator & langs

    # read ios langs
    print '(i) Fetching supported locale codes for ios9 ...'
    __IOS9_CODES__ = [lang_row[0] for lang_row in csv.reader(open(resolve_file_path('lc_ios9.tsv'),'rb'), delimiter='\t')]
    print '(i) Supported numbers of locale code :', len(__IOS9_CODES__)

    __MS_CODE_ALIASES__ = {
        # MS API Supported : ios9 supported ISO639 1-2 codes
        'zh-CHS' : ['zh-Hans', 'zh-CN', 'zh-SG'],
        'zh-CHT' : ['zh-Hant', 'zh-MO', 'zh-HK', 'zh-TW'],
        'en' : ['en-AU', 'en-GB'],
        'es' : ['es-MX'],
        'fr' : ['fr-CA'],
        'pt' : ['pt-BR','pt-PT']
    }

    # read mst langs
    print '(i) Fetching supported locales from Microsoft Translation API...'
    trans = Translator(args['client_id'], args['client_secret'])

    __MS_LANG_FILE__ = resolve_file_path('lc_ms.cached.tsv')
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
    print '(i) Supported numbers of locale code :', len(__MS_SUPPORTED_CODES__)

    # methods
    def supported_lang(code):
        alias = [ms for ms, ios in __MS_CODE_ALIASES__.items() if code in ios]
        # check es-{Custom defined alias}
        if len(alias)==1:
            return alias[0]
        # check es-MX
        elif code in __MS_SUPPORTED_CODES__:
            return code
        # check es
        elif code.split(__LANG_SEP__)[0] in __MS_SUPPORTED_CODES__:
            return code.split(__LANG_SEP__)[0]
        else:
            return None

    def translate_ms(strs, to):
        is_supported = supported_lang(to)
        return [r['TranslatedText'] for r in trans.translate_array(strs, to)] if is_supported else strs

    def strings_obj_from_file(file):
        return localizable.parse_strings(filename=file)

    def merge_two_dicts(x, y):
        '''Given two dicts, merge them into a new dict as a shallow copy.'''
        z = x.copy()
        z.update(y)
        return z

    # core function
    def insert_or_translate(target_file, lc):
        base_content = base_dict[os.path.basename(target_file)]
        base_kv = {}
        for item in base_content:
            base_kv[item['key']] = item['value']

        target_kv = {}
        if not notexist_or_empty_file(target_file):
            for item in localizable.parse_strings(filename=target_file):
                target_kv[item['key']] = item['value']

        adding_keys = list((set(base_kv.keys()) - set(target_kv.keys())) | (set(base_kv.keys()) & set(__FORCE_TRANSLATE__)))
        removing_keys = list(set(target_kv.keys()) - set(base_kv.keys()))
        existing_keys = list(set(base_kv.keys()) - (set(adding_keys) | set(removing_keys)))

        """
        perform translate
        """
        translated_kv = {};
        if len(adding_keys):
            print 'Translating...'
            translated_kv = dict(zip(adding_keys, translate_ms([base_kv[k] for k in adding_keys], lc)))

        updated_content = []
        for item in base_content:
            k = item['key']
            newitem = dict.fromkeys(item.keys())
            newitem['key'] = k

            #added
            if k in adding_keys:
                if k in translated_kv:
                    newitem['value'] = translated_kv[k]
                    print '[Add] "{0}" = "{1}" <- {2}'.format(k, newitem['value'], base_kv[k])
                    newitem['comment'] = 'Translated from: {0}'.format(base_kv[k])
                else:
                    print '[Fail] "{0}" = "{1}" X <- {2}'.format(k, newitem['value'], base_kv[k])
                    newitem['comment'] = 'Translate Failed: {0}'.format(base_kv[k])
            #exists
            elif k in existing_keys:
                newitem['value'] = target_kv[k] if k in target_kv else base_kv[k]

            updated_content.append(newitem)

        #removed or wrong
        for k in removing_keys:
            print '[Remove]', k

        if len(adding_keys) or len(removing_keys):
            print '(i) Changed Keys: Added {0}, Removed {1}'.format(len(adding_keys), len(removing_keys))

        return len(adding_keys)>0 or len(removing_keys)>0, updated_content, translated_kv

    def write_file(target_file, list_of_content):
        suc = False
        try:
            f = codecs.open(target_file, "w", "utf-8")
            contents = ''
            for content in list_of_content:
                if content['comment']:
                    contents += '/* {0} */'.format(content['comment']) + '\n'
                contents += '"{0}" = "{1}";'.format(content['key'], content['value']) + '\n'
            f.write(contents)
            suc = True
        except IOError:
            print 'IOError to open', target_file
        finally:
            f.close()
        return suc

    def remove_file(target_file):
        try:
            os.rename(target_file, target_file+'.deleted')
            return True
        except IOError:
            print 'IOError to rename', target_file
            return False

    def create_file(target_file):
        open(target_file, 'a').close()

    def notexist_or_empty_file(target_file):
        return not os.path.exists(target_file) or os.path.getsize(target_file)==0

    def resolve_file_names(target_file_names):
        return map(lambda f: f.decode('utf-8'), filter(lambda f: f.endswith(__FILE_SUFFIX__), target_file_names))

    base_dict = None
    results_dict = {}

    # Get Base Language Specs

    walked = list(os.walk(__RESOURCE_PATH__, topdown=True))

    for dir, subdirs, files in walked:
        if os.path.basename(dir)==__BASE_RESOUCE_DIR__:
            base_dict = {}
            for _file in resolve_file_names(files):
                f = os.path.join(dir, _file)
                if notexist_or_empty_file(f):
                    continue

                base_dict[_file] = strings_obj_from_file(f)

    if not base_dict:
        print '[!] Not found "{0}" in target path "{1}"'.format(__BASE_RESOUCE_DIR__, __RESOURCE_PATH__)
        sys.exit(0)

    print 'Start synchronizing...'
    for file in base_dict:
        print 'Target:', file

    for dir, subdirs, files in walked:
        files = resolve_file_names(files)

        if dir.endswith((__DIR_SUFFIX__)):
            lc = os.path.basename(dir).split(__DIR_SUFFIX__)[0]
            if lc.find('_'): lc = lc.replace('_', __LANG_SEP__)
            if lc == __BASE_LANG__:
                continue

            if lc in __EXCLUDING_LANGS__:
                print 'Skip: ', lc
                continue

            # lc = supported_lang(lc)
            results_dict[lc] = {
                'deleted_files' : [],
                'added_files' : [],
                'updated_files' : [],
                'skipped_files' : [],
                'translated_files_lines' : []
            }

            if not supported_lang(lc):
                print 'Does not supported: ', lc
                results_dict[lc]['skipped_files'] = join_path_all(dir, files)
                continue

            print '\n', 'Start analayzing localizables... {1} (at {0})'.format(dir, lc)

            added_files = list(set(base_dict.keys()) - set(files))
            removed_files = list(set(files) - set(base_dict.keys()))
            existing_files = list(set(files) - (set(added_files) | set(removed_files)))

            added_files = join_path_all(dir, added_files)
            removed_files = join_path_all(dir, removed_files)
            existing_files = join_path_all(dir, existing_files)

            added_cnt, updated_cnt, removed_cnt = 0, 0, 0
            added_translations_num_of_files = {}

            #remove - file
            for removed_file in removed_files:
                print 'Removing File... {0}'.format(removed_file)
                if remove_file(removed_file):
                    removed_cnt+=1

            #add - file
            for added_file in added_files:
                print 'Adding File... {0}'.format(added_file)
                create_file(added_file)
                u, c, t = insert_or_translate(added_file, lc)
                if u and write_file(added_file, c):
                    added_cnt+=1
                    added_translations_num_of_files[added_file] = t

            #exist - lookup lines
            for ext_file in existing_files:
                u, c, t = insert_or_translate(ext_file, lc)
                if u:
                    print 'Updating File... {0}'.format(ext_file)
                    if write_file(ext_file, c):
                        updated_cnt=+1
                        added_translations_num_of_files[ext_file] = t

            if added_cnt or updated_cnt or removed_cnt:
                print '(i) Changed Files : Added {0}, Updated {1}, Removed {2}'.format(added_cnt, updated_cnt, removed_cnt)

            """
            Results
            """
            results_dict[lc]['deleted_files'] = removed_files
            results_dict[lc]['added_files'] = list(set(added_files) & set(added_translations_num_of_files.keys()))
            results_dict[lc]['updated_files'] = list(set(existing_files) & set(added_translations_num_of_files.keys()))
            results_dict[lc]['translated_files_lines'] = added_translations_num_of_files

    # print total Results
    print ''
    t_file_cnt, t_line_cnt = 0, 0
    file_add_cnt, file_remove_cnt, file_update_cnt, file_skip_cnt = 0,0,0,0

    for lc in results_dict.keys():
        result_lc = results_dict[lc]

        file_add_cnt += len(result_lc['added_files'])
        file_remove_cnt += len(result_lc['deleted_files'])
        file_update_cnt += len(result_lc['updated_files'])
        file_skip_cnt += len(result_lc['skipped_files'])

        for f in result_lc['added_files']: print 'Add',f
        for f in result_lc['deleted_files']: print 'Remove',f
        for f in result_lc['updated_files']: print 'Update',f
        for f in result_lc['skipped_files']: print 'Skip',f

        tfiles = result_lc['translated_files_lines']
        if tfiles:
            # print '============ Results for langcode : {0} ============='.format(lc)
            for f in tfiles:
                t_file_cnt += 1
                if len(tfiles[f]):
                    # print '', f
                    for key in tfiles[f]:
                        t_line_cnt += 1
                        # print key, ' = ', tfiles[f][key]

    print ''
    if file_add_cnt or file_update_cnt or file_remove_cnt or file_skip_cnt:
        print 'New Translated Strings Total : {0}'.format(t_line_cnt)
        print 'Changed Files Total : Added {0}, Updated {1}, Removed {2}, Skipped {3}'.format(file_add_cnt, file_update_cnt, file_remove_cnt, file_skip_cnt)
        print "Synchronized."
    else:
        print "Nothing to translate or add. All resources are synchronized."
    return
