"""Feature premium: Importação de planilhas Excel/CSV."""
from pathlib import Path

import pandas as pd

from src.features.books import BooksCRUD
from src.features.readers import ReadersCRUD
from src.utils.logger import logger


class ImportResult:
    def __init__(self):
        self.total = 0
        self.imported = 0
        self.skipped = 0
        self.errors: list[str] = []

    @property
    def success(self) -> bool:
        return self.imported > 0

    def summary(self) -> str:
        lines = [
            f"Total de linhas: {self.total}",
            f"Importados: {self.imported}",
            f"Ignorados (duplicados/erros): {self.skipped}",
        ]
        if self.errors:
            lines.append(f"Erros: {len(self.errors)}")
            for e in self.errors[:5]:
                lines.append(f"  - {e}")
        return "\n".join(lines)


# Mapeamento de colunas aceitas para livros
BOOK_COLUMN_MAP = {
    # Português
    "n_tombo": "n_tombo", "ntombo": "n_tombo", "tombo": "n_tombo",
    "isbn": "isbn", "isbn13": "isbn",
    "editora": "editora", "publisher": "editora",
    "ano_edicao": "ano_edicao", "anoedicao": "ano_edicao", "ano": "ano_edicao", "year": "ano_edicao",
    "classificacao": "classificacao", "classificação": "classificacao",
    "n_folhas": "n_folhas", "nfolhas": "n_folhas", "folhas": "n_folhas", "pages": "n_folhas",
    "titulo": "titulo", "título": "titulo", "title": "titulo", "titulo_livro": "titulo",
    "autor": "autor", "author": "autor",
    "volume": "volume",
    "data_cadastro": "data_cadastro", "datacadastro": "data_cadastro", "date": "data_cadastro",
    "assunto": "assunto", "subject": "assunto",
}

READER_COLUMN_MAP = {
    "nome": "nome", "name": "nome",
    "telefone": "telefone", "phone": "telefone", "tel": "telefone",
    "email": "email",
    "cpf": "cpf",
    "identidade": "identidade", "identity": "identidade", "rg": "identidade",
    "cep": "cep", "zipcode": "cep",
    "escolaridade": "escolaridade", "schooling": "escolaridade", "escol": "escolaridade",
    "data_nascimento": "data_nascimento", "nascimento": "data_nascimento", "birth": "data_nascimento",
    "endereco": "endereco", "endereço": "endereco", "address": "endereco",
    "data_cadastro": "data_cadastro", "cadastro": "data_cadastro",
}


def _normalize_columns(columns: list[str], col_map: dict) -> dict[int, str]:
    """Mapeia índices de colunas do CSV para campos do banco."""
    mapping = {}
    for i, col in enumerate(columns):
        normalized = col.strip().lower().replace(" ", "_")
        if normalized in col_map:
            mapping[i] = col_map[normalized]
    return mapping


def _read_file(filepath: str) -> pd.DataFrame | None:
    """Lê arquivo Excel ou CSV."""
    path = Path(filepath)
    ext = path.suffix.lower()

    try:
        if ext in (".xlsx", ".xls"):
            return pd.read_excel(filepath, dtype=str)
        elif ext == ".csv":
            for encoding in ["utf-8", "latin-1", "cp1252", "iso-8859-1"]:
                try:
                    return pd.read_csv(filepath, dtype=str, encoding=encoding)
                except UnicodeDecodeError:
                    continue
            return pd.read_csv(filepath, dtype=str)
        else:
            logger.warning("Unsupported file type: {}", ext)
            return None
    except Exception as e:
        logger.error("Error reading file: {}", e)
        return None


def import_books(filepath: str) -> ImportResult:
    """Importa livros de um arquivo Excel/CSV."""
    result = ImportResult()
    df = _read_file(filepath)
    if df is None or df.empty:
        result.errors.append("Arquivo vazio ou inválido.")
        return result

    col_map = _normalize_columns(list(df.columns), BOOK_COLUMN_MAP)
    if not col_map:
        result.errors.append(
            f"Colunas não reconhecidas: {list(df.columns)}. "
            f"Colunas aceitas: {list(set(BOOK_COLUMN_MAP.keys()))}"
        )
        return result

    result.total = len(df)

    # Verificar duplicatas existentes
    existing = {b["n_tombo"] for b in BooksCRUD.read_all()}

    for idx, row in df.iterrows():
        try:
            data = {}
            for csv_col, db_field in col_map.items():
                val = str(row.iloc[csv_col]).strip()
                if val == "nan" or val == "None":
                    val = ""
                data[db_field] = val

            n_tombo = data.get("n_tombo", "")
            if not n_tombo:
                result.errors.append(f"Linha {idx + 2}: Nº Tombo vazio.")
                result.skipped += 1
                continue

            if n_tombo in existing:
                result.skipped += 1
                continue

            titulo = data.get("titulo", "")
            if not titulo:
                result.errors.append(f"Linha {idx + 2}: Título vazio.")
                result.skipped += 1
                continue

            BooksCRUD.create(
                n_tombo=n_tombo,
                isbn=data.get("isbn", ""),
                editora=data.get("editora", ""),
                ano_edicao=data.get("ano_edicao", ""),
                classificacao=data.get("classificacao", ""),
                n_folhas=data.get("n_folhas", ""),
                titulo=titulo,
                autor=data.get("autor", ""),
                volume=data.get("volume", ""),
                data_cadastro=data.get("data_cadastro", ""),
                assunto=data.get("assunto", ""),
            )
            existing.add(n_tombo)
            result.imported += 1

        except Exception as e:
            result.errors.append(f"Linha {idx + 2}: {str(e)[:50]}")
            result.skipped += 1

    logger.info("Books import: {} imported, {} skipped", result.imported, result.skipped)
    return result


def import_readers(filepath: str) -> ImportResult:
    """Importa leitores de um arquivo Excel/CSV."""
    result = ImportResult()
    df = _read_file(filepath)
    if df is None or df.empty:
        result.errors.append("Arquivo vazio ou inválido.")
        return result

    col_map = _normalize_columns(list(df.columns), READER_COLUMN_MAP)
    if not col_map:
        result.errors.append(
            f"Colunas não reconhecidas: {list(df.columns)}. "
            f"Colunas aceitas: {list(set(READER_COLUMN_MAP.keys()))}"
        )
        return result

    result.total = len(df)
    existing = {r["cpf"] for r in ReadersCRUD.read_all()}

    for idx, row in df.iterrows():
        try:
            data = {}
            for csv_col, db_field in col_map.items():
                val = str(row.iloc[csv_col]).strip()
                if val == "nan" or val == "None":
                    val = ""
                data[db_field] = val

            cpf = data.get("cpf", "")
            nome = data.get("nome", "")
            if not nome:
                result.errors.append(f"Linha {idx + 2}: Nome vazio.")
                result.skipped += 1
                continue
            if not cpf:
                result.errors.append(f"Linha {idx + 2}: CPF vazio.")
                result.skipped += 1
                continue

            if cpf in existing:
                result.skipped += 1
                continue

            ReadersCRUD.create(
                nome=nome,
                telefone=data.get("telefone", ""),
                email=data.get("email", ""),
                cpf=cpf,
                identidade=data.get("identidade", ""),
                cep=data.get("cep", ""),
                escolaridade=data.get("escolaridade", ""),
                data_nascimento=data.get("data_nascimento", ""),
                endereco=data.get("endereco", ""),
                data_cadastro=data.get("data_cadastro", ""),
            )
            existing.add(cpf)
            result.imported += 1

        except Exception as e:
            result.errors.append(f"Linha {idx + 2}: {str(e)[:50]}")
            result.skipped += 1

    logger.info("Readers import: {} imported, {} skipped", result.imported, result.skipped)
    return result


def export_template(entity: str, filepath: str) -> bool:
    """Exporta um template vazio para preenchimento."""
    try:
        if entity == "books":
            columns = [
                "n_tombo", "isbn", "editora", "ano_edicao", "classificacao",
                "n_folhas", "titulo", "autor", "volume", "data_cadastro", "assunto",
            ]
            example = [
                "0001", "978-85-359-0295-6", "Companhia das Letras",
                "2019", "Ficção", "352", "Dom Casmurro", "Machado de Assis",
                "1", "2026-07-27", "Romance clássico brasileiro",
            ]
        elif entity == "readers":
            columns = [
                "nome", "telefone", "email", "cpf", "identidade",
                "cep", "escolaridade", "data_nascimento", "endereco", "data_cadastro",
            ]
            example = [
                "João da Silva", "(22) 99999-9999", "joao@email.com",
                "123.456.789-00", "MG-12.345.678", "28600-000",
                "Sup-Completo", "1990-05-15", "Rua Principal, 123", "2026-07-27",
            ]
        else:
            return False

        df = pd.DataFrame([example], columns=columns)
        df.to_excel(filepath, index=False, sheet_name=f"Template_{entity}")
        logger.info("Template exported: {} to {}", entity, filepath)
        return True
    except Exception as e:
        logger.error("Error exporting template: {}", e)
        return False
