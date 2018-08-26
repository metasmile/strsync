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
