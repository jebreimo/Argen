@ECHO off
python "%~dp0\..\..\clapgen\clapgen.py" --test helptext.txt
IF ERRORLEVEL 1 GOTO End
cl /EHsc ParseArguments.cpp
:End
