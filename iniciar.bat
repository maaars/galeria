@echo off
cd /d "%~dp0"
set PY=python
where python >NUL 2>&1 || set PY=py
echo Instalando lo necesario (solo la primera vez)...
%PY% -m pip install --quiet numpy
%PY% -m pip install --quiet pywebview
%PY% app.py
pause
