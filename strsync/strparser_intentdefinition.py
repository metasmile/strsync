# -*- coding: utf-8 -*-

'''
Intents.intentdefinition Parser
'''

import plistlib, re

def __rgetKeyPair(dictionary, key, idKey=None):
    items = []
    for k in dictionary:
        if k == key:
            items.append({"value": str(dictionary[k]), "id": str(dictionary[idKey]) if idKey is not None else None })
        else:
            if isinstance(dictionary[k], list):
                for item in dictionary[k]:
                    items += __rgetKeyPair(item, key, idKey)
            elif isinstance(dictionary[k], dict):
                items += __rgetKeyPair(dictionary[k], key, idKey)
    return items

def __rgetDict(dictionary, key):
    items = []
    for k in dictionary:
        if k == key:
            items.append(dictionary[k])
        else:
            if isinstance(dictionary[k], list):
                for item in dictionary[k]:
                    items += __rgetDict(item, key)
            elif isinstance(dictionary[k], dict):
                items += __rgetDict(dictionary[k], key)
    return items


def parse_strings(file):
    l = plistlib.readPlist(file)

    keys = [
        'INIntentTitle',
        'INIntentDescription',
        # 'INEnumValueDisplayName', # This key already used in 'INEnums'
        'INIntentParameterCombinationTitle',
        'INIntentResponseCodeFormatString',
        'INIntentParameterCombinationSubtitle'
    ]
    enum_items = {}
    for i, enums in enumerate(__rgetDict(l, 'INEnums')):
        for m in enums:
            enum_items[m['INEnumName']] = [
                {
                    'displayName':v['INEnumValueDisplayName'],
                    'id':v['INEnumValueDisplayNameID'],
                    'name':v['INEnumValueName']
                } for v in m['INEnumValues'] if v['INEnumValueDisplayName']
            ]

    enum_params = {e['id']: e['value'] for e in __rgetKeyPair(l, 'INIntentParameterEnumType', 'INIntentParameterName')}

    stringset = []
    for k in keys:
        a = __rgetKeyPair(l, k, k+"ID")
        for kObj in a:
            id, value = kObj['id'], kObj['value']

            if len(value):
                found_enum_params = list(re.finditer('\$\{(.+)\}', value, flags=re.X))
                if found_enum_params:
                    for m in found_enum_params:
                        enum_key = m.group(1)
                        if enum_key in enum_params:
                            for i, e in enumerate(enum_items[enum_params[enum_key]]):
                                enumerated_value = value.replace('${%s}' % enum_key, e['displayName'])
                                enumerated_key = "{}-{}".format(id, e['id'])
                                stringset.append({
                                    'key': enumerated_key,
                                    'value': enumerated_value,
                                    'comment': None,
                                    'error': None}
                                )
                        else:
                            stringset.append({
                                'key': id,
                                'value': value,
                                'comment': None,
                                'error': None}
                            )
                else:
                    stringset.append({
                        'key': id,
                        'value': value,
                        'comment': None,
                        'error': None}
                    )
    return stringset
