"""Ponto de entrada do LIBRYNO v2.0."""
import os
import sys

# Garante que o diretório raiz está no path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.app import run

if __name__ == "__main__":
    run()
