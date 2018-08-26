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
