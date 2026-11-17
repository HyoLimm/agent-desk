@echo off
rem agent-desk: if Python 3.10+ with tkinter is missing, print a one-time install hint for this session.
rem The window and the other hooks run on Python, so this check must not need Python itself.
rem Hooks start in the user's project folder. Never pick up python.* or tkinter.py from there:
rem do not search the current folder for executables, move to the plugin folder, and run Python isolated (-I).
set NoDefaultCurrentDirectoryInExePath=1
cd /d "%~dp0"
python -I -c "import sys, tkinter; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if errorlevel 1 echo {"systemMessage": "agent-desk: Python 3.10 \uc774\uc0c1(tkinter \ud3ec\ud568)\uc774 \uc5c6\uc5b4 \uac10\uc790 \ucc3d\uc744 \ub744\uc6b8 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \uc124\uce58: \ud130\ubbf8\ub110\uc5d0\uc11c winget install Python.Python.3.12 \ub610\ub294 https://www.python.org \uc5d0\uc11c \ubc1b\uae30(\uc124\uce58 \ud654\uba74\uc5d0\uc11c Add python.exe to PATH \uccb4\ud06c). \uc124\uce58\ud55c \ub4a4 \uc0c8 \ucc44\ud305\uc744 \uc5ec\uc138\uc694."}
exit /b 0
