    # -*- coding: utf-8 -*-

import plistlib

def rget(dictionary, key, idKey):
    items = []
    for k in dictionary:
        if k == key:
            items.append({"label": str(dictionary[k]), "id":str(dictionary[idKey])})
        else:
            if isinstance(dictionary[k], list):
                for item in dictionary[k]:
                    items += rget(item, key, idKey)
            elif isinstance(dictionary[k], dict):
                items += rget(dictionary[k], key, idKey)
    return items

l = plistlib.readPlist('/Users/blackgene/Documents/pap/pap/Resources/Intents/Base.lproj/Intents.intentdefinition')

keys = [
    'INIntentTitle',
    'INIntentDescription',
    'INEnumValueDisplayName',
    'INIntentParameterCombinationTitle',
    'INIntentResponseCodeFormatString',
    'INIntentParameterCombinationSubtitle'
]

results = ''
for k in keys:
    a = rget(l, k, k+"ID")
    for kObj in a:
        id, label = kObj['id'], kObj['label']
        if len(label):
            results += '"{}" = "{}";\n'.format(id, label)

print(results)
