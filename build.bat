@echo off
REM ============================================
REM Build Script - Libryno v2.0 Windows
REM ============================================

echo === Build LIBRYNO v2.0 ===
echo.

echo 1. Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller requests-sse
if errorlevel 1 goto error

echo.
echo 2. Executando testes...
python -m pytest tests/ -v --tb=short
if errorlevel 1 goto error

echo.
echo 3. Compilando com PyInstaller...
pyinstaller build.spec --clean --noconfirm --onefile
if errorlevel 1 goto error

echo.
echo 4. Organizando arquivos...
if not exist dist\packages mkdir dist\packages
copy /Y dist\LIBRYNO.exe dist\packages\ 2>nul

echo.
echo === Build concluido! ===
echo Arquivos em: dist/
dir dist\
dir dist\packages\

goto end

:error
echo.
echo ERRO durante o build!
exit /b 1

:end
