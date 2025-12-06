
@echo off
REM Simple CI script: run style & type checks for the repository
REM - Runs pycodestyle but ignores the "line too long" error (E501)
REM - Runs mypy for static type checks
REM Usage: run from repository root: `scripts\ci.bat`

setlocal
set "ERR=0"

echo Running pycodestyle ...
python -m pycodestyle ^
	--ignore=E501 ^
	--show-source --statistics ^
	--exclude=.venv,flicker/assets/resources_rc.py ^
	.

if %ERRORLEVEL% NEQ 0 (
	set "ERR=1"
)

echo Running mypy type checks ...
python -m mypy --exclude "\\.venv|flicker[\\/]+assets[\\/]+resources_rc\\.py" .
if %ERRORLEVEL% NEQ 0 (
	set "ERR=1"
)

if %ERR% EQU 0 (
	echo All checks passed.
	endlocal
	exit /b 0
) else (
	echo One or more checks failed.
	echo If tools are missing, install with: `python -m pip install pycodestyle mypy`
	endlocal
	exit /b 1
)
