cd %HOMEPATH%
powershell -Command "& {Invoke-WebRequest https://www.python.org/ftp/python/3.6.1/python-3.6.1-amd64.exe -usebasicparsing -OutFile python-3.6.1-amd64.exe}"
start /wait python-3.6.1-amd64.exe /quiet InstallAllUsers=1 Include_debug=1 DefaultAllUsersTargetDir=C:\Python3.6
del /F /S /Q python-3.6.1-amd64.exe
