# ============================================
# Build Script - Libryno v2.0
# ============================================
# Uso:
#   Linux:  ./build.sh
#   Windows: build.bat
#
# Dependências:
#   pip install -r requirements.txt
#   pip install pyinstaller

set -e

echo "=== Build LIBRYNO v2.0 ==="

echo ""
echo "1. Instalando dependências..."
pip install -r requirements.txt
pip install pyinstaller requests-sse

echo ""
echo "2. Executando testes..."
python -m pytest tests/ -v --tb=short

echo ""
echo "3. Compilando com PyInstaller..."
pyinstaller build.spec --clean --noconfirm

echo ""
echo "4. Organizando arquivos..."
mkdir -p dist/packages
cp dist/LIBRYNO* dist/packages/ 2>/dev/null || true

echo ""
echo "5. Criando AppImage (Linux)..."
if [ -f dist/LIBRYNO ]; then
    # Cria um script AppImage simples
    echo "#!/bin/bash" > dist/libryno-linux.sh
    echo "exec \"$(pwd)/dist/LIBRYNO\" \"\$@\"" >> dist/libryno-linux.sh
    chmod +x dist/libryno-linux.sh
    mv dist/libryno-linux.sh dist/Libryno-Linux-x86_64.sh
    echo "AppImage criado: dist/Libryno-Linux-x86_64.sh"
fi

echo ""
echo "=== Build concluído! ==="
echo "Arquivos em: dist/"
ls -la dist/

echo ""
echo "Para instalar no Linux (.deb):"
echo "  sudo apt install ./Libryno-Linux-x86_64.sh"
echo ""
echo "Para Windows:"
echo "  dist/LIBRYNO.exe"
