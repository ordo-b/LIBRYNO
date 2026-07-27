"""Sistema de relatórios avançados (PREMIUM)."""
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from src.features.books import BooksCRUD
from src.features.readers import ReadersCRUD
from src.features.loans import LoansCRUD
from src.utils.logger import logger


def _get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="TitleCustom", fontSize=18, spaceAfter=20,
        textColor=colors.HexColor("#5CE1E6"), alignment=1,
    ))
    styles.add(ParagraphStyle(
        name="SubTitle", fontSize=12, spaceAfter=10,
        textColor=colors.HexColor("#666666"), alignment=1,
    ))
    return styles


def generate_books_report(filepath: str) -> bool:
    try:
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = _get_styles()
        elements = []
        elements.append(Paragraph("LIBRYNO - Relatório de Livros", styles["TitleCustom"]))
        elements.append(Paragraph(
            f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles["SubTitle"],
        ))
        elements.append(Spacer(1, 20))

        data = BooksCRUD.read_all()
        if not data:
            elements.append(Paragraph("Nenhum livro cadastrado.", styles["Normal"]))
        else:
            headers = ["Nº Tombo", "Título", "Autor", "Editora", "ISBN"]
            table_data = [headers]
            for b in data:
                table_data.append([
                    b.get("n_tombo", ""), b.get("titulo", "")[:30],
                    b.get("autor", "")[:25], b.get("editora", "")[:20],
                    b.get("isbn", ""),
                ])

            table = Table(table_data, colWidths=[60, 150, 120, 100, 80])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5CE1E6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"Total: {len(data)} livros", styles["Normal"]))

        doc.build(elements)
        logger.info("Books report generated: {}", filepath)
        return True
    except Exception as e:
        logger.error("Error generating books report: {}", e)
        return False


def generate_readers_report(filepath: str) -> bool:
    try:
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = _get_styles()
        elements = []
        elements.append(Paragraph("LIBRYNO - Relatório de Leitores", styles["TitleCustom"]))
        elements.append(Paragraph(
            f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles["SubTitle"],
        ))
        elements.append(Spacer(1, 20))

        data = ReadersCRUD.read_all()
        if not data:
            elements.append(Paragraph("Nenhum leitor cadastrado.", styles["Normal"]))
        else:
            headers = ["Nome", "CPF", "Email", "Telefone"]
            table_data = [headers]
            for r in data:
                table_data.append([
                    r.get("nome", "")[:30], r.get("cpf", ""),
                    r.get("email", "")[:30], r.get("telefone", ""),
                ])

            table = Table(table_data, colWidths=[150, 100, 150, 100])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5CE1E6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"Total: {len(data)} leitores", styles["Normal"]))

        doc.build(elements)
        logger.info("Readers report generated: {}", filepath)
        return True
    except Exception as e:
        logger.error("Error generating readers report: {}", e)
        return False


def generate_loans_report(filepath: str) -> bool:
    try:
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        styles = _get_styles()
        elements = []
        elements.append(Paragraph("LIBRYNO - Relatório de Empréstimos", styles["TitleCustom"]))
        elements.append(Paragraph(
            f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            styles["SubTitle"],
        ))
        elements.append(Spacer(1, 20))

        stats = LoansCRUD.get_stats()
        elements.append(Paragraph(f"Ativos: {stats['active']} | Devolvidos: {stats['returned']} | Atrasados: {stats['overdue']}", styles["Normal"]))
        elements.append(Spacer(1, 10))

        data = LoansCRUD.read_all()
        if not data:
            elements.append(Paragraph("Nenhum empréstimo registrado.", styles["Normal"]))
        else:
            headers = ["Livro", "Leitor", "Saída", "Devolução", "Status", "Multa"]
            table_data = [headers]
            for l in data:
                table_data.append([
                    l.get("livro", "")[:25], l.get("leitor", "")[:25],
                    l.get("data_emprestimo", ""), l.get("data_devolucao_prevista", ""),
                    l.get("status", ""), f"R$ {l.get('multa', 0):.2f}",
                ])

            table = Table(table_data, colWidths=[120, 100, 70, 70, 60, 60])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5CE1E6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elements.append(table)

        doc.build(elements)
        logger.info("Loans report generated: {}", filepath)
        return True
    except Exception as e:
        logger.error("Error generating loans report: {}", e)
        return False
