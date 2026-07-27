"""Sistema de seed data - Dados demo para preencher o banco vazio."""
import random
from datetime import datetime, timedelta
from src.core.database import DatabaseSession
from src.core.models import Book, Reader
from src.features.readers import ReadersCRUD
from src.features.collaborators import CollaboratorsCRUD
from src.utils.logger import logger


DEMO_BOOKS = [
    {"n_tombo": "0001", "isbn": "978-85-359-0295-6", "editora": "Companhia das Letras",
     "ano_edicao": "2019", "classificacao": "Ficção", "n_folhas": "352",
     "titulo": "Dom Casmurro", "autor": "Machado de Assis", "volume": "1",
     "assunto": "Romance clássico da literatura brasileira."},
    {"n_tombo": "0002", "isbn": "978-85-010-0786-4", "editora": "Global Editora",
     "ano_edicao": "2016", "classificacao": "Ficção", "n_folhas": "256",
     "titulo": "O Cortiço", "autor": "Aluísio Azevedo", "volume": "1",
     "assunto": "Romance naturalista brasileiro."},
    {"n_tombo": "0003", "isbn": "978-85-7232-045-3", "editora": "Ática",
     "ano_edicao": "2020", "classificacao": "Ficção", "n_folhas": "160",
     "titulo": "Iracema", "autor": "José de Alencar", "volume": "1",
     "assunto": "Romance indianista."},
    {"n_tombo": "0004", "isbn": "978-65-5561-000-0", "editora": "Editora 34",
     "ano_edicao": "2023", "classificacao": "Ficção", "n_folhas": "412",
     "titulo": "Torto Arado", "autor": "Itamar Vieira Junior", "volume": "1",
     "assunto": "Romance contemporâneo premiado."},
    {"n_tombo": "0005", "isbn": "978-85-359-0736-8", "editora": "Companhia das Letras",
     "ano_edicao": "2022", "classificacao": "Ficção", "n_folhas": "608",
     "titulo": "Grande Sertão: Veredas", "autor": "Guimarães Rosa", "volume": "1",
     "assunto": "Romance modernista."},
    {"n_tombo": "0006", "isbn": "978-85-9431-001-1", "editora": "Penguin-Companhia",
     "ano_edicao": "2021", "classificacao": "Não-ficção", "n_folhas": "224",
     "titulo": "O Pequeno Príncipe", "autor": "Antoine de Saint-Exupéry", "volume": "1",
     "assunto": "Fábula filosófica."},
    {"n_tombo": "0007", "isbn": "978-85-5463-002-2", "editora": "HarperCollins",
     "ano_edicao": "2018", "classificacao": "Ficção", "n_folhas": "680",
     "titulo": "Cem Anos de Solidão", "autor": "Gabriel García Márquez", "volume": "1",
     "assunto": "Realismo mágico."},
    {"n_tombo": "0008", "isbn": "978-85-010-1234-5", "editora": "Rocco",
     "ano_edicao": "2020", "classificacao": "Ficção", "n_folhas": "448",
     "titulo": "A Hora da Estrela", "autor": "Clarice Lispector", "volume": "1",
     "assunto": "Romance existencialista."},
    {"n_tombo": "0009", "isbn": "978-85-7232-567-8", "editora": "Ática",
     "ano_edicao": "2022", "classificacao": "Didático", "n_folhas": "320",
     "titulo": "Matemática para o Ensino Médio", "autor": "Ieda Gomes", "volume": "1",
     "assunto": "Livro didático de matemática."},
    {"n_tombo": "0010", "isbn": "978-85-010-9876-3", "editora": "Editora 34",
     "ano_edicao": "2021", "classificacao": "Poesia", "n_folhas": "96",
     "titulo": "Alguma Poesia", "autor": "Carlos Drummond de Andrade", "volume": "1",
     "assunto": "Coletânea poética."},
    {"n_tombo": "0011", "isbn": "978-85-359-1111-2", "editora": "Companhia das Letras",
     "ano_edicao": "2023", "classificacao": "Ficção", "n_folhas": "280",
     "titulo": "Memórias Póstumas de Brás Cubas", "autor": "Machado de Assis", "volume": "1",
     "assunto": "Romance memorialista."},
    {"n_tombo": "0012", "isbn": "978-85-010-2222-3", "editora": "Alfaguara",
     "ano_edicao": "2019", "classificacao": "Ficção", "n_folhas": "368",
     "titulo": "O Alquimista", "autor": "Paulo Coelho", "volume": "1",
     "assunto": "Fábula filosófica."},
    {"n_tombo": "0013", "isbn": "978-85-7232-333-4", "editora": "Modernista",
     "ano_edicao": "2020", "classificacao": "Técnico", "n_folhas": "480",
     "titulo": "Engenharia de Software", "autor": "Ian Sommerville", "volume": "1",
     "assunto": "Livro técnico sobre engenharia de software."},
    {"n_tombo": "0014", "isbn": "978-85-010-4444-5", "editora": "Record",
     "ano_edicao": "2022", "classificacao": "Ficção", "n_folhas": "520",
     "titulo": "O Livro dos Espíritos", "autor": "Allan Kardec", "volume": "1",
     "assunto": "Espiritismo."},
    {"n_tombo": "0015", "isbn": "978-85-359-5555-6", "editora": "Penguin-Companhia",
     "ano_edicao": "2021", "classificacao": "Referência", "n_folhas": "1200",
     "titulo": "Dicionário Aurélio", "autor": "Aurélio Buarque de Holanda", "volume": "1",
     "assunto": "Dicionário da língua portuguesa."},
    {"n_tombo": "0016", "isbn": "978-85-010-6666-7", "editora": "HarperCollins",
     "ano_edicao": "2023", "classificacao": "Ficção", "n_folhas": "304",
     "titulo": "1984", "autor": "George Orwell", "volume": "1",
     "assunto": "Distopia."},
    {"n_tombo": "0017", "isbn": "978-85-7232-777-8", "editora": "Ática",
     "ano_edicao": "2022", "classificacao": "Didático", "n_folhas": "256",
     "titulo": "Português para o Ensino Médio", "autor": "Cecília Marconi", "volume": "1",
     "assunto": "Gramática e interpretação textual."},
    {"n_tombo": "0018", "isbn": "978-85-010-8888-9", "editora": "Rocco",
     "ano_edicao": "2021", "classificacao": "Infantil", "n_folhas": "48",
     "titulo": "O Monstro das Cores", "autor": "Anna Llenas", "volume": "1",
     "assunto": "Literatura infantil sobre emoções."},
    {"n_tombo": "0019", "isbn": "978-85-359-9999-0", "editora": "Companhia das Letras",
     "ano_edicao": "2020", "classificacao": "Ficção", "n_folhas": "384",
     "titulo": "Vidas Secas", "autor": "Graciliano Ramos", "volume": "1",
     "assunto": "Romance regionalista."},
    {"n_tombo": "0020", "isbn": "978-85-010-1111-1", "editora": "Editora 34",
     "ano_edicao": "2023", "classificacao": "Crônica", "n_folhas": "192",
     "titulo": "Contos", "autor": "Lygia Fagundes Telles", "volume": "1",
     "assunto": "Coletânea de contos."},
]

DEMO_READERS = [
    {"nome": "Maria Clara Santos", "telefone": "(22) 99876-5432", "email": "maria.clara@email.com",
     "cpf": "123.456.789-00", "identidade": "MG-12.345.678", "cep": "28600-000",
     "escolaridade": "Sup-Completo", "data_nascimento": "1995-03-15", "endereco": "Rua das Flores, 123"},
    {"nome": "João Pedro Oliveira", "telefone": "(22) 99765-4321", "email": "joao.pedro@email.com",
     "cpf": "987.654.321-00", "identidade": "RJ-98.765.432", "cep": "28610-000",
     "escolaridade": "Medio-Completo", "data_nascimento": "1988-07-22", "endereco": "Av. Brasil, 456"},
    {"nome": "Ana Beatriz Lima", "telefone": "(22) 99654-3210", "email": "ana.beatriz@email.com",
     "cpf": "456.789.123-00", "identidade": "ES-45.678.901", "cep": "28620-000",
     "escolaridade": "Sup-Cursando", "data_nascimento": "2001-11-08", "endereco": "Rua do Sol, 789"},
    {"nome": "Carlos Eduardo Souza", "telefone": "(22) 99543-2109", "email": "carlos.ed@email.com",
     "cpf": "321.654.987-00", "identidade": "SP-32.165.498", "cep": "28630-000",
     "escolaridade": "Fund-Completo", "data_nascimento": "1975-01-30", "endereco": "Rua da Paz, 321"},
    {"nome": "Fernanda Costa", "telefone": "(22) 99432-1098", "email": "fernanda@email.com",
     "cpf": "654.321.987-00", "identidade": "RJ-65.432.198", "cep": "28640-000",
     "escolaridade": "Sup-Completo", "data_nascimento": "1992-06-12", "endereco": "Av. Central, 654"},
    {"nome": "Lucas Henrique Alves", "telefone": "(22) 99321-0987", "email": "lucas.h@email.com",
     "cpf": "789.123.456-00", "identidade": "MG-78.901.234", "cep": "28650-000",
     "escolaridade": "Medio-Cursando", "data_nascimento": "2003-09-05", "endereco": "Rua Nova, 987"},
    {"nome": "Juliana Mendes", "telefone": "(22) 99210-9876", "email": "juliana.m@email.com",
     "cpf": "147.258.369-00", "identidade": "RJ-14.258.369", "cep": "28660-000",
     "escolaridade": "Sup-Completo", "data_nascimento": "1985-12-25", "endereco": "Rua da Liberdade, 147"},
    {"nome": "Rafael Martins", "telefone": "(22) 99109-8765", "email": "rafael.m@email.com",
     "cpf": "258.369.147-00", "identidade": "BA-25.836.914", "cep": "28670-000",
     "escolaridade": "Medio-Completo", "data_nascimento": "1990-04-18", "endereco": "Rua do Comércio, 258"},
    {"nome": "Patrícia Nascimento", "telefone": "(22) 99098-7654", "email": "patricia.n@email.com",
     "cpf": "369.147.258-00", "identidade": "PE-36.914.725", "cep": "28680-000",
     "escolaridade": "Sup-Cursando", "data_nascimento": "1998-08-03", "endereco": "Av. Paulista, 369"},
    {"nome": "Thiago Fernandes", "telefone": "(22) 98987-6543", "email": "thiago.f@email.com",
     "cpf": "963.852.741-00", "identidade": "RJ-96.385.274", "cep": "28690-000",
     "escolaridade": "Incompleto", "data_nascimento": "1982-02-14", "endereco": "Rua Velha, 963"},
    {"nome": "Camila Rodrigues", "telefone": "(22) 98876-5432", "email": "camila.r@email.com",
     "cpf": "852.741.963-00", "identidade": "SP-85.274.196", "cep": "28700-000",
     "escolaridade": "Sup-Completo", "data_nascimento": "1993-10-20", "endereco": "Rua das Acácias, 852"},
    {"nome": "Bruno Azevedo", "telefone": "(22) 98765-4321", "email": "bruno.a@email.com",
     "cpf": "741.963.852-00", "identidade": "MG-74.196.385", "cep": "28710-000",
     "escolaridade": "Medio-Completo", "data_nascimento": "1987-05-07", "endereco": "Av. das Américas, 741"},
    {"nome": "Amanda Ribeiro", "telefone": "(22) 98654-3210", "email": "amanda.r@email.com",
     "cpf": "963.741.852-00", "identidade": "RJ-96.374.185", "cep": "28720-000",
     "escolaridade": "Sup-Cursando", "data_nascimento": "2000-01-11", "endereco": "Rua dos Pinhais, 963"},
    {"nome": "Diego Santos", "telefone": "(22) 98543-2109", "email": "diego.s@email.com",
     "cpf": "159.753.486-00", "identidade": "BA-15.975.348", "cep": "28730-000",
     "escolaridade": "Fund-Completo", "data_nascimento": "1978-09-28", "endereco": "Rua da Fonte, 159"},
    {"nome": "Letícia Barbosa", "telefone": "(22) 98432-1098", "email": "leticia.b@email.com",
     "cpf": "753.486.159-00", "identidade": "ES-75.348.615", "cep": "28740-000",
     "escolaridade": "Sup-Completo", "data_nascimento": "1996-07-16", "endereco": "Av. Beira Mar, 753"},
    {"nome": "Gustavo Moreira", "telefone": "(22) 98321-0987", "email": "gustavo.m@email.com",
     "cpf": "486.159.753-00", "identidade": "RJ-48.615.975", "cep": "28750-000",
     "escolaridade": "Medio-Cursando", "data_nascimento": "2002-03-09", "endereco": "Rua das Laranjeiras, 486"},
    {"nome": "Isabela Carvalho", "telefone": "(22) 98210-9876", "email": "isabela.c@email.com",
     "cpf": "321.486.159-00", "identidade": "MG-32.148.615", "cep": "28760-000",
     "escolaridade": "Sup-Completo", "data_nascimento": "1991-12-01", "endereco": "Rua da Cidade, 321"},
    {"nome": "Pedro Henrique Gomes", "telefone": "(22) 98109-8765", "email": "pedro.h@email.com",
     "cpf": "159.321.486-00", "identidade": "RJ-15.932.148", "cep": "28770-000",
     "escolaridade": "Medio-Completo", "data_nascimento": "1989-06-22", "endereco": "Av. Atlântica, 159"},
    {"nome": "Renata Dias", "telefone": "(22) 98098-7654", "email": "renata.d@email.com",
     "cpf": "486.321.159-00", "identidade": "SP-48.632.115", "cep": "28780-000",
     "escolaridade": "Sup-Cursando", "data_nascimento": "1999-04-05", "endereco": "Rua do Porto, 486"},
    {"nome": "Marcos Vinícius Pereira", "telefone": "(22) 97987-6543", "email": "marcos.v@email.com",
     "cpf": "654.987.321-00", "identidade": "MG-65.498.732", "cep": "28790-000",
     "escolaridade": "Incompleto", "data_nascimento": "1980-08-17", "endereco": "Rua Velha, 654"},
]


def seed_demo_data():
    """Preenche o banco com dados demo se estiver vazio."""
    with DatabaseSession() as session:
        book_count = session.query(Book).count()
        reader_count = session.query(Reader).count()

    if book_count > 0 or reader_count > 0:
        logger.info("Database already has data ({} books, {} readers), skipping seed",
                     book_count, reader_count)
        return False

    logger.info("Seeding demo data...")

    # Seed books
    for book_data in DEMO_BOOKS:
        book_data["data_cadastro"] = (
            datetime.now() - timedelta(days=random.randint(1, 365))
        ).strftime("%Y-%m-%d")
        BooksCRUD.create(**book_data)

    # Seed readers
    for reader_data in DEMO_READERS:
        reader_data["data_cadastro"] = (
            datetime.now() - timedelta(days=random.randint(1, 365))
        ).strftime("%Y-%m-%d")
        ReadersCRUD.create(**reader_data)

    # Seed admin (if not exists)
    CollaboratorsCRUD.create("Administrador", "admin", "admin123", "admin")

    logger.info("Demo data seeded: {} books, {} readers", len(DEMO_BOOKS), len(DEMO_READERS))
    return True
