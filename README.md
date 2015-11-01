# transync
Automatically translate and synchronize '.strings' files from defined base language.


## Requirements

### Install

```
pip install transync
```

### To use Microsoft Translation API

You should do several requirements.

#### Getting your client id/secret id

To register your application with Azure DataMarket, visit https://datamarket.azure.com/developer/applications/ using the LiveID credentials from step 1, and click on “Register”. In the “Register your application” dialog box, you can define your own Client ID and Name. The redirect URI is not used for the Microsoft Translator API. However, the redirect URI field is a mandatory field, and you must provide a URI to obtain the access code. A description is optional.
Take a note of the client ID and the client secret value.

#### Update python SSL packages

this is not required for python-2.7.9+

```shell
pip install requests[security]
```
This installs following extra packages:
```
pyOpenSSL
ndg-httpsclient
pyasn1
```

