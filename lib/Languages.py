from Constants import *


class Language:
    id = 0
    display_name = "Abstract Language"


class PythonLanguage(Language):
    id = 1
    display_name = PYTHON_DISPLAY_NAME


class CSharpLanguage(Language):
    id = 2
    display_name = CSHARP_DISPLAY_NAME


LANGUAGES = {1: PythonLanguage, 2: CSharpLanguage}