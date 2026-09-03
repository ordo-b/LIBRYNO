"""Tela de importação por cola — copiar/colar dados de tabela.

Suporta:
- Dados copiados de planilhas (separados por tab)
- CSV colado (separados por vírgula)
- Dados de sistemas antigos

Funciona no plano FREE com limite de 20 linhas.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.auth.session import session
from src.features.books import BooksCRUD
from src.features.import_data import import_books, import_readers
from src.features.premium_promo import promo_manager
from src.features.readers import ReadersCRUD
from src.ui.i18n.translator import t
from src.utils.constants import FREE_MAX_BOOKS, FREE_MAX_READERS
from src.utils.logger import logger


class ImportPasteScreen(QWidget):
    """Tela de importação por cola — alternativa ao upload de arquivo."""

    FREE_ROW_LIMIT = 20

    def __init__(self, entity_type: str = "books", on_complete=None):
        super().__init__()
        self.entity_type = entity_type
        self.on_complete = on_complete
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        title = QLabel(f"📥 Importar {t(self.entity_type + '.title')}")
        title.setObjectName("title")
        layout.addWidget(title)

        # Mode selector
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Formato dos dados:")
        mode_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        mode_layout.addWidget(mode_label)

        self.combo_mode = QComboBox()
        self.combo_mode.addItems([
            "📋 Colar dados (Tab)",
            "📝 Colar CSV (vírgula)",
            "📁 Importar arquivo",
        ])
        self.combo_mode.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.combo_mode)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # FREE tier info
        if not session.is_premium:
            info = QLabel(
                f"💡 Plano FREE: até {self.FREE_ROW_LIMIT} linhas por importação. "
                "Faça upgrade para importar ilimitado."
            )
            info.setStyleSheet(
                "color: #FFD700; font-size: 11px; background: transparent; "
                "padding: 8px; border: 1px solid #FFD700; border-radius: 4px;"
            )
            info.setWordWrap(True)
            layout.addWidget(info)

        # Paste area
        paste_label = QLabel("Cole os dados abaixo:")
        paste_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        layout.addWidget(paste_label)

        self.text_paste = QTextEdit()
        self.text_paste.setPlaceholderText(
            "Cole aqui os dados copiados de uma planilha...\n\n"
            "Exemplo (separados por tab):\n"
            "0001\t978-85-359-0295-6\tCompanhia das Letras\t2019\tFicção\t352\tDom Casmurro\tMachado de Assis\n"
            "0002\t978-85-010-0786-4\tGlobal Editora\t2016\tFicção\t256\tO Cortiço\tAluísio Azevedo"
        )
        self.text_paste.setMinimumHeight(150)
        layout.addWidget(self.text_paste)

        # Preview table
        preview_frame = QFrame()
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(0, 0, 0, 0)

        self.preview_label = QLabel("📊 Pré-visualização:")
        self.preview_label.setStyleSheet("color: #cccccc; font-size: 12px;")
        preview_layout.addWidget(self.preview_label)

        self.preview_text = QLabel("Nenhuma dados colados ainda.")
        self.preview_text.setStyleSheet(
            "color: #888; font-size: 11px; padding: 8px; "
            "background: #16213e; border-radius: 4px;"
        )
        self.preview_text.setWordWrap(True)
        self.preview_text.setMinimumHeight(60)
        preview_layout.addWidget(self.preview_text)

        layout.addWidget(preview_frame)

        # Buttons
        btn_layout = QHBoxLayout()

        btn_parse = QPushButton("🔍 Analisar Dados")
        btn_parse.setFixedHeight(36)
        btn_parse.clicked.connect(self._parse_data)
        btn_layout.addWidget(btn_parse)

        self.btn_import = QPushButton(f"📥 Importar {t(self.entity_type + '.title')}")
        self.btn_import.setFixedHeight(36)
        self.btn_import.setEnabled(False)
        self.btn_import.clicked.connect(self._do_import)
        btn_layout.addWidget(self.btn_import)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #a0a0a0; font-size: 11px;")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Internal state
        self._parsed_data = []
        self._file_mode = False

    def _on_mode_changed(self, index):
        if index == 2:  # File mode
            self._file_mode = True
            self.text_paste.setEnabled(False)
            self.text_paste.setPlaceholderText("Selecione um arquivo usando o botão abaixo...")
            self._open_file_dialog()
        else:
            self._file_mode = False
            self.text_paste.setEnabled(True)
            self.text_paste.clear()

    def _open_file_dialog(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            f"Importar {t(self.entity_type + '.title')}",
            "",
            "Planilhas (*.xlsx *.xls *.csv);;Todos os arquivos (*)",
        )
        if filepath:
            self.text_paste.setPlainText(f"📁 Arquivo selecionado: {filepath}")
            self._parse_file(filepath)
        else:
            self.combo_mode.setCurrentIndex(0)

    def _parse_file(self, filepath: str):
        """Importa arquivo diretamente."""
        if self.entity_type == "books":
            result = import_books(filepath)
        else:
            result = import_readers(filepath)

        if result.success:
            self.preview_text.setText(
                f"✅ {result.imported} registros importados de arquivo.\n"
                f"⏭ {result.skipped} ignorados | 📊 Total: {result.total}"
            )
            self.btn_import.setEnabled(False)
            self.status_label.setText("✅ Importação concluída!")
            promo_manager.register_import()
            if self.on_complete:
                self.on_complete()
        else:
            self.preview_text.setText(
                f"❌ Erro na importação:\n" + "\n".join(result.errors[:3])
            )

    def _parse_data(self):
        """Analisa os dados colados."""
        if self._file_mode:
            return

        raw = self.text_paste.toPlainText().strip()
        if not raw:
            self.preview_text.setText("❌ Nenhum dado para analisar.")
            return

        lines = raw.strip().split("\n")

        # Detectar separador
        first_line = lines[0]
        if "\t" in first_line:
            separator = "\t"
            sep_name = "Tab"
        elif "," in first_line:
            separator = ","
            sep_name = "Vírgula"
        elif ";" in first_line:
            separator = ";"
            sep_name = "Ponto e vírgula"
        else:
            separator = "\t"
            sep_name = "Tab (padrão)"

        # Parse
        self._parsed_data = []
        errors = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(separator)]
            if len(parts) < 2:
                errors.append(f"Linha {i + 1}: poucos campos ({len(parts)})")
                continue
            self._parsed_data.append(parts)

        # Preview
        if self._parsed_data:
            preview_lines = [
                f"📊 {len(self._parsed_data)} linhas detectadas (separador: {sep_name})"
            ]
            for row in self._parsed_data[:3]:
                preview_lines.append(f"  → {' | '.join(row[:5])}")
            if len(self._parsed_data) > 3:
                preview_lines.append(f"  ... e mais {len(self._parsed_data) - 3} linhas")

            if errors:
                preview_lines.append(f"\n⚠️ {len(errors)} linhas com erro")

            self.preview_text.setText("\n".join(preview_lines))
            self.btn_import.setEnabled(True)
            self.status_label.setText(
                f"✅ {len(self._parsed_data)} registros prontos para importar"
            )
        else:
            self.preview_text.setText("❌ Nenhum dado válido encontrado.")
            self.btn_import.setEnabled(False)

    def _do_import(self):
        """Executa a importação dos dados colados."""
        if not self._parsed_data:
            return

        # Verificar limite FREE
        if not session.is_premium:
            max_rows = self.FREE_ROW_LIMIT
            if len(self._parsed_data) > max_rows:
                reply = QMessageBox.question(
                    self,
                    "Limite FREE",
                    f"Plano FREE permite até {max_rows} linhas.\n"
                    f"Você tem {len(self._parsed_data)} linhas.\n\n"
                    f"As primeiras {max_rows} serão importadas.\n"
                    f"Faça upgrade para importar todas.",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply == QMessageBox.Yes:
                    self._parsed_data = self._parsed_data[:max_rows]
                else:
                    return

        # Converter para formato de importação
        import tempfile
        import csv
        from pathlib import Path

        if self.entity_type == "books":
            headers = [
                "n_tombo", "isbn", "editora", "ano_edicao", "classificacao",
                "n_folhas", "titulo", "autor", "volume", "data_cadastro", "assunto",
            ]
        else:
            headers = [
                "nome", "telefone", "email", "cpf", "identidade",
                "cep", "escolaridade", "data_nascimento", "endereco", "data_cadastro",
            ]

        # Criar CSV temporário
        tmp = Path(tempfile.gettempdir()) / f"libryno_import_{self.entity_type}.csv"
        with open(tmp, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in self._parsed_data:
                # Preencher colunas faltantes
                padded = row + [""] * (len(headers) - len(row))
                writer.writerow(padded[:len(headers)])

        # Importar
        if self.entity_type == "books":
            result = import_books(str(tmp))
        else:
            result = import_readers(str(tmp))

        # Limpar temporário
        try:
            tmp.unlink()
        except Exception:
            pass

        if result.success:
            self.preview_text.setText(
                f"✅ Importação concluída!\n"
                f"📥 {result.imported} registros importados\n"
                f"⏭ {result.skipped} ignorados"
            )
            self.btn_import.setEnabled(False)
            self.status_label.setText("✅ Sucesso!")
            promo_manager.register_import()
            if self.on_complete:
                self.on_complete()
        else:
            self.preview_text.setText(
                f"⚠️ Importação parcial:\n"
                f"✅ {result.imported} importados\n"
                f"❌ {len(result.errors)} erros\n\n"
                + "\n".join(result.errors[:5])
            )
