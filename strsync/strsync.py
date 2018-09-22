# -*- coding: utf-8 -*-
# strsync - Automatically translate and synchronize .strings files from defined base language.
# Copyright (c) 2015 metasmile cyrano905@gmail.com (github.com/metasmile)

from __future__ import print_function
import strparser, strlocale, strtrans
import time, os, sys, argparse, codecs, csv
from os.path import expanduser
from fuzzywuzzy import fuzz
from colorama import init
from colorama import Fore, Back, Style
import unicodedata2

init(autoreset=True)


def len_unicode(ustr):
    return len(unicodedata2.normalize('NFC', ustr.decode('utf-8')))


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
    parser = argparse.ArgumentParser(
        description='Automatically translate and synchronize .strings files from defined base language.')
    parser.add_argument('-b', '--base-lang-name',
                        help='A base(or source) localizable resource name.(default=\'Base\'), (e.g. "Base" via \'Base.lproj\', "en" via \'en.lproj\')',
                        default='Base', required=False)
    parser.add_argument('-x', '--excluding-lang-names', type=str,
                        help='A localizable resource name that you want to exclude. (e.g. "Base" via \'Base.lproj\', "en" via \'en.lproj\')',
                        default=[], required=False, nargs='+')
    parser.add_argument('-f', '--force-translate-keys', type=str,
                        help='Keys in the strings to update and translate by force. (input nothing for all keys.)',
                        default=[], required=False, nargs='*')
    parser.add_argument('-o', '--following-base-keys', type=str, help='Keys in the strings to follow from "Base.',
                        default=[], required=False, nargs='+')
    parser.add_argument('-w', '--following-base-if-not-exists', type=str, help='With this option, all keys will be followed up with base values if they does not exist.',
                        default=None, required=False, nargs='*')
    parser.add_argument('-l', '--cutting-length-ratio-with-base', type=float,
                        help='Keys in the float as the ratio to compare the length of "Base"',
                        default=[], required=False, nargs='+')
    parser.add_argument('-c', '--ignore-comments', help='Allows ignoring comment synchronization.', default=None,
                        required=False, nargs='*')
    parser.add_argument('-v', '--verify-results', help='Verify translated results via reversed results', default=None,
                        required=False, nargs='*')
    parser.add_argument('-s', '--include-secondary-languages', help='Include Additional Secondary Languages. (+63 language codes)', default=None,
                        required=False, nargs='*')
    parser.add_argument('-i', '--ignore-unverified-results',
                        help='Allows ignoring unverified results when appending them.', default=None, required=False,
                        nargs='*')
    parser.add_argument('target path', help='Target localization resource path. (root path of Base.lproj, default=./)',
                        default='./', nargs='?')
    args = vars(parser.parse_args())

    reload(sys)
    sys.setdefaultencoding('utf-8')

    # configure arguments
    __LOCALE_XCODE_BASE_LOWERCASE__ = 'base'

    __DIR_SUFFIX__ = ".lproj"
    __FILE_SUFFIX__ = ".strings"
    __FILE_DICT_SUFFIX__ = ".stringsdict"
    __RESOURCE_PATH__ = expanduser(args['target path'])
    __BASE_LANG__ = args['base_lang_name']
    __EXCLUDING_LANGS__ = args['excluding_lang_names']
    __KEYS_FORCE_TRANSLATE__ = args['force_translate_keys']
    __KEYS_FORCE_TRANSLATE_ALL__ = ('--force-translate-keys' in sys.argv or '-f' in sys.argv) and not __KEYS_FORCE_TRANSLATE__
    __KEYS_FOLLOW_BASE__ = args['following_base_keys']
    __CUTTING_LENGTH_RATIO__ = (args['cutting_length_ratio_with_base'] or [0])[0]
    __FOLLOWING_ALL_KEYS_IFNOT_EXIST__ = args['following_base_if_not_exists'] is not None

    __IGNORE_COMMENTS__ = args['ignore_comments'] is not None
    __IGNORE_UNVERIFIED_RESULTS__ = args['ignore_unverified_results'] is not None
    __RATIO_TO_IGNORE_UNVERIFIED_RESULTS__ = int(
        args['ignore_unverified_results'][0]) if __IGNORE_UNVERIFIED_RESULTS__ and len(
        args['ignore_unverified_results']) else 0
    __VERIFY_TRANS_RESULTS__ = __IGNORE_UNVERIFIED_RESULTS__ or args['verify_results'] is not None
    __INCLUDE_SECONDARY_LANGUAGES__ = args['include_secondary_languages'] is not None

# Locale settings
    # [language designator] en, fr
    # [language designator]_[region designator] en_GB, zh_HK
    # [language designator]-[script designator] az-Arab, zh-Hans
    # [language designator]-[script designator]_[region designator] zh-Hans_HK
    print('(i) Initializing for supported languages ...')
    __lang_codes = strlocale.default_supporting_xcode_lang_codes()

    if __INCLUDE_SECONDARY_LANGUAGES__:
        __lang_codes += strlocale.secondary_supporting_xcode_lang_codes()

    __XCODE_LPROJ_SUPPORTED_LOCALES_MAP__ = strlocale.map_locale_codes(__lang_codes, strtrans.supported_locale_codes())
    __XCODE_LPROJ_SUPPORTED_LOCALES__ = __XCODE_LPROJ_SUPPORTED_LOCALES_MAP__.keys()
    print(Fore.WHITE + '(i) Supported numbers of locale code :', str(len(__XCODE_LPROJ_SUPPORTED_LOCALES__)),
          Style.RESET_ALL)
    print(__XCODE_LPROJ_SUPPORTED_LOCALES__)

    # handle base
    if __BASE_LANG__.endswith(__DIR_SUFFIX__):
        __BASE_RESOUCE_DIR__ = __BASE_LANG__
        __BASE_LANG__ = __BASE_LANG__.split(__DIR_SUFFIX__)[0]
    else:
        __BASE_RESOUCE_DIR__ = __BASE_LANG__ + __DIR_SUFFIX__

    if not __BASE_LANG__.lower() == __LOCALE_XCODE_BASE_LOWERCASE__:
        __BASE_LANG__ = strlocale.lang(__BASE_LANG__)

    # setup Translator & langs

    # read ios langs
    print(Fore.WHITE + '(i) Fetching supported locale codes for ios9 ...', Style.RESET_ALL)
    __IOS9_CODES__ = [lang_row[0] for lang_row in
                      csv.reader(open(resolve_file_path('lc_ios9.tsv'), 'rb'), delimiter='\t')]
    print(Fore.WHITE + '(i) Supported numbers of locale code :', len(__IOS9_CODES__), Style.RESET_ALL)

    global_result_logs = {}

    def strings_obj_from_file(file):
        return strparser.parse_strings(filename=file)

    def merge_two_dicts(x, y):
        '''Given two dicts, merge them into a new dict as a shallow copy.'''
        z = x.copy()
        z.update(y)
        return z

    # core function
    def insert_or_translate(target_file, lc):
        # parse target file
        target_kv = {}
        target_kc = {}
        target_error_lines = []
        if not notexist_or_empty_file(target_file):
            parsed_strings = strparser.parse_strings(filename=target_file)
            for item in parsed_strings:
                k, e = item['key'], item['error']
                # line error
                if e:
                    target_error_lines.append(e)
                if not target_error_lines:
                    target_kv[k] = item['value']
                    target_kc[k] = item['comment']

        # parsing complete or return.
        if target_error_lines:
            print('(!) Syntax error - Skip')
            return False, None, None, target_error_lines

        # base
        base_content = base_dict[os.path.basename(target_file)]
        base_kv = {}
        base_kc = {}
        for item in base_content:
            k, e = item['key'], item['error']
            # line error
            if e:
                print('(!) WARNING : Syntax error from Base -> ', k, ':', e)
            base_kv[k] = item['value']
            base_kc[k] = item['comment']

        force_adding_keys = base_kv.keys() if __KEYS_FORCE_TRANSLATE_ALL__ else __KEYS_FORCE_TRANSLATE__

        adding_keys = list(
            ((set(base_kv.keys()) - set(target_kv.keys())) | (set(base_kv.keys()) & set(force_adding_keys))) \
            - set(base_kv.keys() if __FOLLOWING_ALL_KEYS_IFNOT_EXIST__ else __KEYS_FOLLOW_BASE__) \
        )

        removing_keys = list(set(target_kv.keys()) - set(base_kv.keys()))
        existing_keys = list(set(base_kv.keys()) - (set(adding_keys) | set(removing_keys)))
        updated_keys = []

        """
        perform translate
        """
        translated_kv = {}
        reversed_matched_kv = {}  # {"ratio":float, "ignored":True|False}
        reversed_translated_kv = {}
        if len(adding_keys):
            print('Translating...')
            translated_kv = dict(zip(adding_keys, strtrans.translate_strs([base_kv[k] for k in adding_keys], lc)))

            if __VERIFY_TRANS_RESULTS__:
                print('Reversing results and matching...')
                reversed_translated_kv = dict(
                    zip(adding_keys, strtrans.translate_strs([translated_kv[_ak] for _ak in adding_keys], 'en')))

                for bk in adding_keys:
                    if bk in reversed_translated_kv:
                        ratio = fuzz.partial_ratio(base_kv[bk], reversed_translated_kv[bk])
                        should_ignore = __IGNORE_UNVERIFIED_RESULTS__ and ratio <= __RATIO_TO_IGNORE_UNVERIFIED_RESULTS__
                        if should_ignore:
                            translated_kv[bk] = base_kv[bk]  # copy from base set
                        reversed_matched_kv[bk] = {"ratio": ratio, "ignored": should_ignore}

        updated_content = []
        for item in base_content:
            k = item['key']
            newitem = dict.fromkeys(item.keys())
            newitem['key'] = k
            target_value, target_comment = target_kv.get(k), target_kc.get(k)
            newitem['comment'] = target_comment if __IGNORE_COMMENTS__ else target_comment or base_kc[k]
            needs_update_comment = False if __IGNORE_COMMENTS__ else not target_comment and base_kc[k]

            # added
            if k in adding_keys:
                if k in translated_kv:
                    newitem['value'] = translated_kv[k]
                    if not newitem['comment']:
                        newitem['comment'] = 'Translated from: {0}'.format(base_kv[k])

                    reversed_matched_msg = ''
                    if k in reversed_matched_kv:
                        reversed_matched_msg = Fore.CYAN + "({}% Matched{}: \'{}\' <- \'{}\' <- \'{}\')".format(
                            reversed_matched_kv[k]["ratio"],
                            ", So ignored [X]" if reversed_matched_kv[k]["ignored"] else "", reversed_translated_kv[k],
                            newitem['value'], base_kv[k]) + Style.RESET_ALL

                    print('[Add] "{0}" = "{1}" <- {2}'.format(k, newitem['value'], base_kv[k]), reversed_matched_msg)
                else:
                    newitem['value'] = target_kv[k]
                    if not newitem['comment']:
                        newitem['comment'] = 'Translate failed from: {0}'.format(base_kv[k])

                    print(Fore.RED + '[Error] "{0}" = "{1}" X <- {2}'.format(k, newitem['value'],
                                                                             base_kv[k]) + Style.RESET_ALL)

            # exists
            elif k in existing_keys:

                if k != "Base" and __CUTTING_LENGTH_RATIO__>0:

                    if target_value != base_kv[k] \
                            and len_unicode(target_value) > float(len_unicode(base_kv[k]))*__CUTTING_LENGTH_RATIO__ \
                            or needs_update_comment:

                        print(Fore.YELLOW + '(!) Length of "', target_value, '" is longer than"', base_kv[k], '" as',
                              len(target_value), '>', len(base_kv[k]), Style.RESET_ALL)
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

        # removed or wrong
        for k in removing_keys:
            print(Fore.RED + '[Remove]', k, Style.RESET_ALL)

        if len(adding_keys) or len(updated_keys) or len(removing_keys):
            print(Fore.WHITE + '(i) Changed Keys: Added {0}, Updated {1}, Removed {2}'.format(len(adding_keys),
                                                                                              len(updated_keys),
                                                                                              len(removing_keys)),
                  Style.RESET_ALL)

        # check verification failed items
        target_verified_items = None
        if len(reversed_matched_kv):
            target_verified_items = {
                k: {'ratio': reversed_matched_kv[k]["ratio"], 'original': base_kv[k],
                    'reversed': reversed_translated_kv[k],
                    'translated': translated_kv[k]} for k in reversed_matched_kv.keys()}

        return updated_content and (len(adding_keys) > 0 or len(updated_keys) > 0 or len(
            removing_keys) > 0), updated_content, translated_kv, target_error_lines, target_verified_items

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
            print('IOError to open', target_file)
        finally:
            f.close()
        return suc

    def remove_file(target_file):
        try:
            os.rename(target_file, target_file + '.deleted')
            return True
        except IOError:
            print('IOError to rename', target_file)
            return False

    def create_file(target_file):
        open(target_file, 'a').close()

    def notexist_or_empty_file(target_file):
        return not os.path.exists(target_file) or os.path.getsize(target_file) == 0

    def resolve_file_names(target_file_names):
        return map(lambda f: f.decode('utf-8'), filter(lambda f: f.endswith(__FILE_SUFFIX__), target_file_names))

    base_dict = {}
    results_dict = {}

    # Get Base Language Specs
    walked = list(os.walk(__RESOURCE_PATH__, topdown=True))

    # Init with Base.lproj
    for dir, subdirs, files in walked:
        if os.path.basename(dir) == __BASE_RESOUCE_DIR__:
            for _file in resolve_file_names(files):
                f = os.path.join(dir, _file)
                if notexist_or_empty_file(f):
                    continue

                parsed_obj = strings_obj_from_file(f)
                if not parsed_obj:
                    continue

                base_dict[_file] = parsed_obj

    if not base_dict:
        print('[!] Not found "{0}" in target path "{1}"'.format(__BASE_RESOUCE_DIR__, __RESOURCE_PATH__))
        sys.exit(0)

    # Exist or Create supporting lproj dirs.
    print('Check and verifiy resources ...')
    current_lproj_names = [os.path.splitext(os.path.basename(lproj_path))[0] for lproj_path in
                           filter(lambda d: d.endswith(__DIR_SUFFIX__), [dir for dir, subdirs, files in walked])]
    notexisted_lproj_names = list(set(__XCODE_LPROJ_SUPPORTED_LOCALES__) - set(current_lproj_names))

    creating_lproj_dirs = [expanduser(os.path.join(__RESOURCE_PATH__, ln + __DIR_SUFFIX__)) for ln in
                           notexisted_lproj_names]
    if creating_lproj_dirs:
        print('Following lproj dirs does not exists. Creating ...')
        for d in creating_lproj_dirs:
            print('Created', d)
            os.mkdir(d)

    # Start to sync localizable files.
    print('Start synchronizing...')
    for file in base_dict:
        print('Target:', file)

    for dir, subdirs, files in walked:
        files = resolve_file_names(files)

        if dir.endswith((__DIR_SUFFIX__)):
            lproj_name = os.path.basename(dir).split(__DIR_SUFFIX__)[0]

            if lproj_name == __BASE_LANG__:
                continue

            if not lproj_name in __XCODE_LPROJ_SUPPORTED_LOCALES_MAP__:
                print('Does not supported: ', lproj_name)
                continue

            lc = __XCODE_LPROJ_SUPPORTED_LOCALES_MAP__[lproj_name]

            if strlocale.matched_locale_code(lc, __EXCLUDING_LANGS__):
                print('Skip: ', lc)
                continue

            results_dict[lc] = {
                'deleted_files': [],
                'added_files': [],
                'updated_files': [],
                'skipped_files': [],
                'translated_files_lines': {},
                'error_lines_kv': {},
                'verified_result': {}
            }

            # if not supported_lang(lc):
            #     print('Does not supported: ', lc)
            #     results_dict[lc]['skipped_files'] = join_path_all(dir, files)
            #     continue

            print('\n', 'Analayzing localizables... {1} (at {0})'.format(dir, lc))

            added_files = list(set(base_dict.keys()) - set(files))
            removed_files = list(set(files) - set(base_dict.keys()))
            existing_files = list(set(files) - (set(added_files) | set(removed_files)))

            added_files = join_path_all(dir, added_files)
            removed_files = join_path_all(dir, removed_files)
            existing_files = join_path_all(dir, existing_files)

            added_cnt, updated_cnt, removed_cnt = 0, 0, 0
            translated_files_lines = results_dict[lc]['translated_files_lines']
            error_files = results_dict[lc]['error_lines_kv']

            # remove - file
            for removed_file in removed_files:
                print('Removing File... {0}'.format(removed_file))
                if remove_file(removed_file):
                    removed_cnt += 1

            # add - file
            for added_file in added_files:
                print('Adding File... {0}'.format(added_file))
                create_file(added_file)
                u, c, t, e, m = insert_or_translate(added_file, lc)
                # error
                if e:
                    error_files[added_file] = e
                # normal
                elif u and write_file(added_file, c):
                    added_cnt += 1
                    translated_files_lines[added_file] = t

                # verify failed
                for k in (m or {}):
                    results_dict[lc]['verified_result'][k] = m[k]

            # exist - lookup lines
            for ext_file in existing_files:
                u, c, t, e, m = insert_or_translate(ext_file, lc)
                # error
                if e:
                    error_files[ext_file] = e
                # normal
                elif u:
                    print('Updating File... {0}'.format(ext_file))
                    if write_file(ext_file, c):
                        updated_cnt = +1
                        translated_files_lines[ext_file] = t

                # verify failed
                for k in (m or {}):
                    results_dict[lc]['verified_result'][k] = m[k]

            if added_cnt or updated_cnt or removed_cnt or error_files:
                print(Fore.WHITE + '(i) Changed Files : Added {0}, Updated {1}, Removed {2}, Error {3}'.format(
                    added_cnt, updated_cnt, removed_cnt, len(error_files.keys())), Style.RESET_ALL)
            else:
                print('Nothing to translate or add.')

            """
            Results
            """
            results_dict[lc]['deleted_files'] = removed_files
            results_dict[lc]['added_files'] = list(set(added_files) & set(translated_files_lines.keys()))
            results_dict[lc]['updated_files'] = list(set(existing_files) & set(translated_files_lines.keys()))
            if error_files:
                print(error_files)
            results_dict[lc]['error_lines_kv'] = error_files

    # print(total Results)
    print('')
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

        for f in result_lc['added_files']: print('Added', f)
        for f in result_lc['deleted_files']: print('Removed', f)
        for f in result_lc['updated_files']: print('Updated', f)
        for f in result_lc['skipped_files']: print('Skiped', f)

        tfiles = result_lc['translated_files_lines']
        if tfiles:
            # print('============ Results for langcode : {0} ============='.format(lc))
            for f in tfiles:
                t_file_cnt += 1
                if len(tfiles[f]):
                    # print('', f)
                    for key in tfiles[f]:
                        t_line_cnt += 1
                        # print(key, ' = ', tfiles[f][key])

    for lc in global_result_logs.keys():
        print(lc)
        for t in global_result_logs[lc].keys():
            o, b = global_result_logs[lc][t]
            print(o.decode('utf-8'), ' -> ', b)

    print('')
    # WARN
    found_warining = filter(lambda i: i or None, rget(results_dict, 'error_lines_kv'))
    if found_warining:
        print(
            Fore.YELLOW + '\n[!] WARNING: Found strings that contains the syntax error. Please confirm.' + Style.RESET_ALL)
        for a in found_warining:
            for k in a:
                print('at', k)
                for i in a[k]:
                    print(' ', i)
    # VERIFY FAILED
    verified_results = filter(lambda i: i or None, rget(results_dict, 'verified_result'))
    if verified_results and len(verified_results):
        print(
            Fore.GREEN + '\n[i] VERIFIED RESULTS: Matched ratio via reversed translation results. Please confirm.' + Style.RESET_ALL)
        for lc in results_dict:
            print(lc)
            vr = results_dict[lc]['verified_result']
            for k in vr:
                vd = vr[k]
                status_msg = Fore.RED + '(Ignored) ' + Style.RESET_ALL if __IGNORE_UNVERIFIED_RESULTS__ and vd[
                    'ratio'] <= __RATIO_TO_IGNORE_UNVERIFIED_RESULTS__ else ''

                print('  {}{}: {} -> {} -> {}, Matched: {}%'.format(status_msg, k
                                                                    , vd['original']
                                                                    , vd['translated']
                                                                    , vd['reversed']
                                                                    , str(vd['ratio'])))

    print('')
    if file_add_cnt or file_update_cnt or file_remove_cnt or file_skip_cnt:
        print('Total New Translated Strings : {0}'.format(t_line_cnt))
        print('Changed Files Total : Added {0}, Updated {1}, Removed {2}, Skipped {3}'.format(file_add_cnt,
                                                                                              file_update_cnt,
                                                                                              file_remove_cnt,
                                                                                              file_skip_cnt))
        print("Synchronized.")
    else:
        print("All strings are already synchronized. Nothing to translate or add.")

    return
