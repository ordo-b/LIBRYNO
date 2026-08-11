"""Otimização de imagens do sistema.

Analisa todas as imagens em img/ e gera relatório de otimização.
"""
from pathlib import Path

IMG_DIR = Path(__file__).resolve().parent.parent.parent / "img"


def analyze_images() -> dict:
    """Analisa todas as imagens e retorna informações de tamanho/formato."""
    results = {}
    if not IMG_DIR.exists():
        return results

    for img_path in IMG_DIR.rglob("*"):
        if img_path.is_file() and img_path.suffix.lower() in (".png", ".jpg", ".jpeg", ".ico", ".svg"):
            size_kb = img_path.stat().st_size / 1024
            results[str(img_path.relative_to(IMG_DIR))] = {
                "size_kb": round(size_kb, 1),
                "format": img_path.suffix.lower(),
                "needs_optimization": size_kb > 100,
            }

    return results


def get_optimization_report() -> str:
    """Gera relatório de otimização das imagens."""
    images = analyze_images()
    if not images:
        return "Nenhuma imagem encontrada."

    lines = ["=== Relatório de Imagens ===\n"]
    total_size = 0
    large_files = []

    for name, info in sorted(images.items()):
        size = info["size_kb"]
        total_size += size
        status = "⚠ GRANDE" if info["needs_optimization"] else "✓ OK"
        lines.append(f"  {status} {name}: {size} KB ({info['format']})")
        if info["needs_optimization"]:
            large_files.append(name)

    lines.append(f"\nTotal: {len(images)} imagens, {total_size:.1f} KB")
    lines.append(f"Arquivos grandes (>100KB): {len(large_files)}")

    if large_files:
        lines.append("\nRecomendações de otimização:")
        for f in large_files:
            lines.append(f"  - Converter {f} para formato WebP ou reduzir resolução")

    return "\n".join(lines)
