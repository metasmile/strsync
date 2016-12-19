# -*- coding: utf-8 -*-
# strsync - Automatically translate and synchronize .strings files from defined base language.
# Copyright (c) 2015 metasmile cyrano905@gmail.com (github.com/metasmile)

from microsofttranslator import Translator
import strsparser
import time, os, sys, re, textwrap, argparse, pprint, subprocess, codecs, csv
from os.path import expanduser
from fuzzywuzzy import fuzz
from colorama import init
from colorama import Fore, Back, Style
init(autoreset=True)

import unicodedata
__UNILEN__ = lambda _str: len(unicodedata.normalize('NFC',_str.decode('utf-8')))

def resolve_file_path(file):
    return os.path.join(os.path.dirname(__file__), file)

def join_path_all(target_dir, target_files):
    return map(lambda f: os.path.join(target_dir, f), target_files)

def rget(dictionary, key):
    items = []
    if key in dictionary:
        items.append(dictionary[key])
    for dict_value in [value for value in dictionary.values() if isinstance(value, dict)]:
        items += rget(dict_value, key)
    return items

def main():
    parser = argparse.ArgumentParser(description='Automatically translate and synchronize .strings files from defined base language.')
    parser.add_argument('-b','--base-lang-name', help='A base(or source) localizable resource name.(default=\'Base\'), (e.g. "Base" via \'Base.lproj\', "en" via \'en.lproj\')', default='Base', required=False)
    parser.add_argument('-x','--excluding-lang-names', type=str, help='A localizable resource name that you want to exclude. (e.g. "Base" via \'Base.lproj\', "en" via \'en.lproj\')', default=[], required=False, nargs='+')
    parser.add_argument('-c','--client-id', help='Client ID for MS Translation API', required=True)
    parser.add_argument('-s','--client-secret', help='Client Secret key for MS Translation API', required=True)
    parser.add_argument('-f','--force-translate-keys', type=str, help='Keys in the strings to update and translate by force. (input nothing for all keys.)', default=[], required=False, nargs='*')
    parser.add_argument('-fb','--following-base-keys', type=str, help='Keys in the strings to follow from "Base".', default=[], required=False, nargs='+')
    parser.add_argument('-fbl','--following-base-keys-if-length-longer', type=str, help='Keys in the strings to follow from "Base" if its length longer than length of "Base" value.', default=[], required=False, nargs='+')
    parser.add_argument('-ic','--ignore-comments', help='Allows to ignore comment synchronization.', default=None, required=False, nargs='*')
    parser.add_argument('-v','--verify-results', help='Verify translated results via reversed results', default=None, required=False, nargs='*')
    parser.add_argument('-iuv','--ignore-unverified-results', help='Allows to ignore unverified results when append them.', default=None, required=False, nargs='*')
    parser.add_argument('target path', help='Target localizable resource path. (root path of Base.lproj, default=./)', default='./', nargs='?')
    args = vars(parser.parse_args())

    reload(sys)
    sys.setdefaultencoding('utf-8')

    # configure arguments
    __LANG_SEP__ = '-'
    __DIR_SUFFIX__ = ".lproj"
    __FILE_SUFFIX__ = ".strings"
    __RESOURCE_PATH__ = expanduser(args['target path'])
    __BASE_LANG__ = args['base_lang_name']
    __EXCLUDING_LANGS__ = args['excluding_lang_names']
    __KEYS_FORCE_TRANSLATE__ = args['force_translate_keys']
    __KEYS_FORCE_TRANSLATE_ALL__ = ('--force-translate-keys' in sys.argv or '-f' in sys.argv) and not __KEYS_FORCE_TRANSLATE__
    __KEYS_FOLLOW_BASE__ = args['following_base_keys']
    __KEYS_FOLLOW_BASE_IF_LENGTH_LONGER__ = args['following_base_keys_if_length_longer']
    __IGNORE_COMMENTS__ = args['ignore_comments'] is not None
    __IGNORE_UNVERIFIED_RESULTS__ = args['ignore_unverified_results'] is not None
    __RATIO_TO_IGNORE_UNVERIFIED_RESULTS__ = int(args['ignore_unverified_results'][0]) if __IGNORE_UNVERIFIED_RESULTS__ and len(args['ignore_unverified_results']) else 0
    __VERIFY_TRANS_RESULTS__ = __IGNORE_UNVERIFIED_RESULTS__ or args['verify_results'] is not None
    __BASE_RESOUCE_DIR__ = None
    # sys.exit(0)
    # return

    __LITERNAL_FORMAT__ = "%@"
    __LITERNAL_FORMAT_RE__ = re.compile(r"(%\s{1,}@)|(@\s{0,}%)")
    __LITERNAL_REPLACEMENT__ = "**"
    __LITERNAL_REPLACEMENT_RE__ = re.compile(r"\*\s{0,}\*")

    __QUOTES_RE__ = re.compile(r"\"")
    __QUOTES_REPLACEMENT__ = "'"

    if __BASE_LANG__.endswith(__DIR_SUFFIX__):
        __BASE_RESOUCE_DIR__ = __BASE_LANG__
        __BASE_LANG__ = __BASE_LANG__.split(__DIR_SUFFIX__)[0]
    else:
        __BASE_RESOUCE_DIR__ = __BASE_LANG__+__DIR_SUFFIX__

    # setup Translator & langs

    # read ios langs
    print Fore.WHITE + '(i) Fetching supported locale codes for ios9 ...' ,Style.RESET_ALL
    __IOS9_CODES__ = [lang_row[0] for lang_row in csv.reader(open(resolve_file_path('lc_ios9.tsv'),'rb'), delimiter='\t')]
    print Fore.WHITE + '(i) Supported numbers of locale code :', len(__IOS9_CODES__) ,Style.RESET_ALL

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
    print Fore.WHITE + '(i) Fetching supported locales from Microsoft Translation API...' ,Style.RESET_ALL
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
    print Fore.WHITE + '(i) Supported numbers of locale code :', len(__MS_SUPPORTED_CODES__) ,Style.RESET_ALL

    #
    global_result_logs = {}

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

    def preprocessing_translate_strs(strs):
        return [__LITERNAL_FORMAT_RE__.sub(__LITERNAL_FORMAT__, s.strip()).replace(__LITERNAL_FORMAT__, __LITERNAL_REPLACEMENT__) for s in strs]

    def postprocessing_translate_str(str):
        str = str.strip()
        # remove Quotes
        str = __QUOTES_RE__.sub(__QUOTES_REPLACEMENT__, str)
        # replace tp liternal replacement
        str = validate_liternal_replacement(str)
        # liternal replacement to liternal for format
        str = str.replace(__LITERNAL_REPLACEMENT__, __LITERNAL_FORMAT__)
        return str

    def validate_liternal_format(str):
        return __LITERNAL_FORMAT_RE__.sub(__LITERNAL_FORMAT__, str)

    def validate_liternal_replacement(str):
        return __LITERNAL_REPLACEMENT_RE__.sub(__LITERNAL_FORMAT__, str)

    def translate_ms(strs, to):
        lang = supported_lang(to)
        strs = preprocessing_translate_strs(strs)
        return [postprocessing_translate_str(r['TranslatedText']) for r in trans.translate_array(strs, lang)] if lang else strs

    def strings_obj_from_file(file):
        return strsparser.parse_strings(filename=file)

    def merge_two_dicts(x, y):
        '''Given two dicts, merge them into a new dict as a shallow copy.'''
        z = x.copy()
        z.update(y)
        return z

    # core function
    def insert_or_translate(target_file, lc):
        #parse target file
        target_kv = {}
        target_kc = {}
        target_error_lines = []
        if not notexist_or_empty_file(target_file):
            parsed_strings = strsparser.parse_strings(filename=target_file)
            for item in parsed_strings:
                k, e = item['key'], item['error']
                # line error
                if e:
                    target_error_lines.append(e)
                if not target_error_lines:
                    target_kv[k] = item['value']
                    target_kc[k] = item['comment']

        #parsing complete or return.
        if target_error_lines:
            print '(!) Syntax error - Skip'
            return False, None, None, target_error_lines

        #base
        base_content = base_dict[os.path.basename(target_file)]
        base_kv = {}
        base_kc = {}
        for item in base_content:
            k, e = item['key'], item['error']
            # line error
            if e:
                print '(!) WARNING : Syntax error from Base -> ', k, ':' , e
            base_kv[k] = item['value']
            base_kc[k] = item['comment']

        force_adding_keys = base_kv.keys() if __KEYS_FORCE_TRANSLATE_ALL__ else __KEYS_FORCE_TRANSLATE__
        adding_keys = list(((set(base_kv.keys()) - set(target_kv.keys())) | (set(base_kv.keys()) & set(force_adding_keys))) - set(__KEYS_FOLLOW_BASE__))
        removing_keys = list(set(target_kv.keys()) - set(base_kv.keys()))
        existing_keys = list(set(base_kv.keys()) - (set(adding_keys) | set(removing_keys)))
        updated_keys = []

        """
        perform translate
        """
        translated_kv = {}
        reversed_matched_ratio_kv = {}
        reversed_translated_kv = {}
        if len(adding_keys):
            print 'Translating...'
            translated_kv = dict(zip(adding_keys, translate_ms([base_kv[k] for k in adding_keys], lc)))

            if __VERIFY_TRANS_RESULTS__:
                print 'Reversing results and matching...'
                reversed_translated_kv = dict(zip(adding_keys, translate_ms(translated_kv.values(), 'en')))
                for bk in adding_keys:
                    if bk in reversed_translated_kv:
                        ratio = fuzz.partial_ratio(base_kv[bk], reversed_translated_kv[bk])
                        if __IGNORE_UNVERIFIED_RESULTS__ and ratio <= __RATIO_TO_IGNORE_UNVERIFIED_RESULTS__:
                            translated_kv[k] = base_kv[k] # copy from base set
                            # adding_keys.remove(bk)
                            print 'Ignored:', bk, '<- Matching ratio: ', ratio
                        reversed_matched_ratio_kv[bk] = ratio

        updated_content = []
        for item in base_content:
            k = item['key']
            newitem = dict.fromkeys(item.keys())
            newitem['key'] = k
            target_value, target_comment = target_kv.get(k), target_kc.get(k)
            newitem['comment'] = target_comment if __IGNORE_COMMENTS__ else target_comment or base_kc[k]
            needs_update_comment = False if __IGNORE_COMMENTS__ else not target_comment and base_kc[k]

            #added
            if k in adding_keys:
                if k in translated_kv:
                    newitem['value'] = translated_kv[k]
                    if not newitem['comment']:
                        newitem['comment'] = 'Translated from: {0}'.format(base_kv[k])

                    reversed_matched_msg = ''
                    if k in reversed_matched_ratio_kv:
                        reversed_matched_msg = Fore.CYAN+"( {} % Matched: \'{}\' <- \'{}\' <- \'{}\' )".format(reversed_matched_ratio_kv[k], reversed_translated_kv[k], newitem['value'], base_kv[k])+Style.RESET_ALL

                    print '[Add] "{0}" = "{1}" <- {2}'.format(k, newitem['value'], base_kv[k]), reversed_matched_msg
                else:
                    newitem['value'] = target_kv[k]
                    if not newitem['comment']:
                        newitem['comment'] = 'Translate failed from: {0}'.format(base_kv[k])

                    print Fore.RED+'[Error] "{0}" = "{1}" X <- {2}'.format(k, newitem['value'], base_kv[k])+Style.RESET_ALL
            #exists
            elif k in existing_keys:

                if k in __KEYS_FOLLOW_BASE_IF_LENGTH_LONGER__:
                    if target_value != base_kv[k] and __UNILEN__(target_value) > __UNILEN__(base_kv[k]) or needs_update_comment:
                        print Fore.YELLOW+'(!) Length of "', target_value, '" is longer than"', base_kv[k], '" as', len(target_value), '>', len(base_kv[k]), Style.RESET_ALL
                        newitem['value'] = base_kv[k]
                        updated_keys.append(k)

                        if not lc in global_result_logs:
                            global_result_logs[lc] = {}
                        global_result_logs[lc][k] = (target_value, base_kv[k])
                    else:
                        newitem['value'] = target_value or base_kv[k]

                elif k in __KEYS_FOLLOW_BASE__:
                    newitem['value'] = base_kv[k]
                    if target_value != base_kv[k] or needs_update_comment:
                        updated_keys.append(k)

                else:
                    newitem['value'] = target_value or base_kv[k]
                    if not target_value or needs_update_comment:
                        updated_keys.append(k)

            updated_content.append(newitem)

        #removed or wrong
        for k in removing_keys:
            print Fore.RED+'[Remove]', k,Style.RESET_ALL

        if len(adding_keys) or len(updated_keys) or len(removing_keys):
            print Fore.WHITE + '(i) Changed Keys: Added {0}, Updated {1}, Removed {2}'.format(len(adding_keys), len(updated_keys), len(removing_keys)) ,Style.RESET_ALL

        #check verification failed items
        target_verified_items = None
        if len(reversed_matched_ratio_kv):
            #filter(lambda k: reversed_matched_ratio_kv[k] < 1, reversed_matched_ratio_kv)
            target_verified_items = {k: {'ratio': reversed_matched_ratio_kv[k], 'original': base_kv[k], 'reversed':reversed_translated_kv[k], 'translated':translated_kv[k] } for k in reversed_matched_ratio_kv.keys()}

        return updated_content and (len(adding_keys)>0 or len(updated_keys)>0 or len(removing_keys)>0), updated_content, translated_kv, target_error_lines, target_verified_items

    def write_file(target_file, list_of_content):
        suc = False
        try:
            f = codecs.open(target_file, "w", "utf-8")
            contents = ''
            for content in list_of_content:
                if content['comment']:
                    contents += '/*{0}*/'.format(content['comment']) + '\n'
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

    base_dict = {}
    results_dict = {}

    # Get Base Language Specs

    walked = list(os.walk(__RESOURCE_PATH__, topdown=True))

    for dir, subdirs, files in walked:
        if os.path.basename(dir)==__BASE_RESOUCE_DIR__:
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
                'translated_files_lines' : {},
                'error_lines_kv' : {},
                'verified_result' : {}
            }

            if not supported_lang(lc):
                print 'Does not supported: ', lc
                results_dict[lc]['skipped_files'] = join_path_all(dir, files)
                continue

            print '\n', 'Analayzing localizables... {1} (at {0})'.format(dir, lc)

            added_files = list(set(base_dict.keys()) - set(files))
            removed_files = list(set(files) - set(base_dict.keys()))
            existing_files = list(set(files) - (set(added_files) | set(removed_files)))

            added_files = join_path_all(dir, added_files)
            removed_files = join_path_all(dir, removed_files)
            existing_files = join_path_all(dir, existing_files)

            added_cnt, updated_cnt, removed_cnt = 0, 0, 0
            translated_files_lines = results_dict[lc]['translated_files_lines']
            error_files = results_dict[lc]['error_lines_kv']

            #remove - file
            for removed_file in removed_files:
                print 'Removing File... {0}'.format(removed_file)
                if remove_file(removed_file):
                    removed_cnt+=1

            #add - file
            for added_file in added_files:
                print 'Adding File... {0}'.format(added_file)
                create_file(added_file)
                u, c, t, e, m = insert_or_translate(added_file, lc)
                #error
                if e:
                    error_files[added_file] = e
                #normal
                elif u and write_file(added_file, c):
                    added_cnt+=1
                    translated_files_lines[added_file] = t

                #verify failed
                for k in (m or {}):
                    results_dict[lc]['verified_result'][k] = m[k]

            #exist - lookup lines
            for ext_file in existing_files:
                u, c, t, e, m = insert_or_translate(ext_file, lc)
                #error
                if e:
                    error_files[ext_file] = e
                #normal
                elif u:
                    print 'Updating File... {0}'.format(ext_file)
                    if write_file(ext_file, c):
                        updated_cnt=+1
                        translated_files_lines[ext_file] = t

                #verify failed
                for k in (m or {}):
                    results_dict[lc]['verified_result'][k] = m[k]

            if added_cnt or updated_cnt or removed_cnt or error_files:
                print Fore.WHITE + '(i) Changed Files : Added {0}, Updated {1}, Removed {2}, Error {3}'.format(added_cnt, updated_cnt, removed_cnt, len(error_files.keys())) ,Style.RESET_ALL
            else:
                print 'Nothing to translate or add.'

            """
            Results
            """
            results_dict[lc]['deleted_files'] = removed_files
            results_dict[lc]['added_files'] = list(set(added_files) & set(translated_files_lines.keys()))
            results_dict[lc]['updated_files'] = list(set(existing_files) & set(translated_files_lines.keys()))
            if error_files:
                print error_files
            results_dict[lc]['error_lines_kv'] = error_files

    # print total Results
    print ''
    t_file_cnt = \
    t_line_cnt = \
    file_add_cnt = \
    file_add_cnt = \
    file_remove_cnt = \
    file_update_cnt = \
    file_skip_cnt = \
    0

    for lc in results_dict.keys():
        result_lc = results_dict[lc]

        file_add_cnt += len(result_lc['added_files'])
        file_remove_cnt += len(result_lc['deleted_files'])
        file_update_cnt += len(result_lc['updated_files'])
        file_skip_cnt += len(result_lc['skipped_files'])

        for f in result_lc['added_files']: print 'Added',f
        for f in result_lc['deleted_files']: print 'Removed',f
        for f in result_lc['updated_files']: print 'Updated',f
        for f in result_lc['skipped_files']: print 'Skiped',f

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

    for lc in global_result_logs.keys():
        print lc
        for t in global_result_logs[lc].keys():
            o, b = global_result_logs[lc][t]
            print o.decode('utf-8'), ' -> ', b

    print ''
    #WARN
    found_warining = filter(lambda i: i or None, rget(results_dict, 'error_lines_kv'))
    if found_warining:
        print Fore.YELLOW+'\n[!] WARNING: Found strings that contains the syntax error. Please confirm.'+Style.RESET_ALL
        for a in found_warining:
            for k in a:
                print 'at', k
                for i in a[k]:
                    print ' ', i
    #VERIFY FAILED
    verified_results = filter(lambda i: i or None, rget(results_dict, 'verified_result'))
    if verified_results and len(verified_results):
        print Fore.GREEN+'\n[i] VERIFIED RESULTS: Matched ratio via reversed translation results. Please confirm.'+Style.RESET_ALL
        for lc in results_dict:
            print lc
            vr = results_dict[lc]['verified_result']
            for k in vr:
                vd = vr[k]
                status_msg = Fore.RED + '(Ignored) '+Style.RESET_ALL if __IGNORE_UNVERIFIED_RESULTS__ and vd['ratio']<=__RATIO_TO_IGNORE_UNVERIFIED_RESULTS__ else ''
                print '  {}{}: {} -> {} -> {}, Matched: {}%'.format(status_msg, k, vd['original'], vd['translated'], vd['reversed'], str(vd['ratio']))

    print ''
    if file_add_cnt or file_update_cnt or file_remove_cnt or file_skip_cnt:
        print 'Total New Translated Strings : {0}'.format(t_line_cnt)
        print 'Changed Files Total : Added {0}, Updated {1}, Removed {2}, Skipped {3}'.format(file_add_cnt, file_update_cnt, file_remove_cnt, file_skip_cnt)
        print "Synchronized."
    else:
        print "All strings are already synchronized. Nothing to translate or add."

    return
