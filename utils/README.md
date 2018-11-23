# genL10N

Extracting all localizable strings from Swift code to Localizable.strings file.

1. Add swift extension
```swift
extension String {
    public var localized: String {
        return NSLocalizedString(self, comment: "")
    }

    public func localizedFormatted(_ arguments: CVarArg...) -> String {
        return withVaList(arguments) {
            return NSString(format: self.localized, arguments: $0) as String
        }
    }
}
```

2. Use .localized extension in everywhere 
```swift
//SomeSwiftFile.swift

376:  if let anysyntax = getMessage("any string to localized".localized) {
377:         //Do something
378:  }
```

3. Insert bash shell into to Xcode Build Phase
```bash
$(which python) ./genl10n.py \
                ./MyProj/ \
                ./MyProj/Resources/Localizations/Base.lproj/Localizable.strings -k .localized
```

4. Results on Base.lproj/Localizable.strings
```
/* Generated from genl10n: SomeSwiftFile.swift#376 */
"any string to localized" = "any string to localized";
~
```

# genUsrL10N

genusrl10n.py lets developer can parse/convert user's translation files into Xcode project's localizable resource file such as Localizable.strings. Only modified values of existed keys in Localizable.strings file will be changed.  

Source file name format should be:
```text
/dir/{locale code to match with Localizable}_XXXXXX.txt

e.g: fr_ContributorName(email.com).txt
```


1. An example from user's translation file.

The content of fr_XXXXX.txt

```text
Reverse
= Sens inverse

Select this photo
= Sélectionnez cette photo

Write
= Écrire
```

The content of ./myProject/Resources/Localizations/fr.lproj/Localizable.strings

```text
"Reverse" = "Some wrongly translated french string";
"Select this photo" = "Some wrongly translated french string";
"Write" = "Some wrongly translated french string";
```

2. To perform this tool

```bash
python ./genusrl10n.py ./userl10n/ ./myProject/Resources/Localizations/
```

3. Result

```text
"Reverse" = "Sens inverse";
"Select this photo" = "Sélectionnez cette photo";
"Write" = "Écrire";
```