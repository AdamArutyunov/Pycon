from Constants import *


class Language:
    id = -1
    display_name = "Abstract Language"
    main_commands = []


class PythonLanguage(Language):
    id = 1
    display_name = PYTHON_DISPLAY_NAME
    main_commands = [PYTHON_COMMAND]


class CSharpLanguage(Language):
    id = 2
    display_name = CSHARP_DISPLAY_NAME
    main_commands = [CSHARP_COMPILE_COMMAND, CSHARP_RUN_COMMAND]


language_association = [None, PythonLanguage, CSharpLanguage]