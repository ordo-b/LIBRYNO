"""Modelos do banco de dados SQLite."""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, ForeignKey, DateTime
)
from sqlalchemy.orm import relationship
from src.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(50), unique=True, nullable=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    token = Column(Text, nullable=True)
    role = Column(String(50), default="user")
    organization_name = Column(String(255), nullable=True)
    license_key = Column(String(100), nullable=True)
    license_status = Column(String(50), nullable=True)
    license_expires_at = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    n_tombo = Column(String(50), unique=True, nullable=False)
    isbn = Column(String(20), nullable=True)
    editora = Column(String(255), nullable=True)
    ano_edicao = Column(String(10), nullable=True)
    classificacao = Column(String(100), nullable=True)
    n_folhas = Column(String(10), nullable=True)
    titulo = Column(String(500), nullable=False)
    autor = Column(String(500), nullable=True)
    volume = Column(String(50), nullable=True)
    data_cadastro = Column(String(20), nullable=True)
    assunto = Column(Text, nullable=True)
    cover_image = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)
    synopsis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    loans = relationship("Loan", back_populates="book", cascade="all, delete-orphan")


class Reader(Base):
    __tablename__ = "readers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    telefone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    cpf = Column(String(20), unique=True, nullable=False)
    identidade = Column(String(30), nullable=True)
    cep = Column(String(10), nullable=True)
    escolaridade = Column(String(50), nullable=True)
    data_nascimento = Column(String(20), nullable=True)
    endereco = Column(String(500), nullable=True)
    data_cadastro = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    loans = relationship("Loan", back_populates="reader", cascade="all, delete-orphan")


class Collaborator(Base):
    __tablename__ = "collaborators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    nome_usuario = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="collaborator")
    created_at = Column(DateTime, default=datetime.utcnow)


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    reader_id = Column(Integer, ForeignKey("readers.id"), nullable=False)
    data_emprestimo = Column(String(20), nullable=False)
    data_devolucao_prevista = Column(String(20), nullable=False)
    data_devolucao_real = Column(String(20), nullable=True)
    status = Column(String(20), default="active")
    multa = Column(Float, default=0.0)
    observacoes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    book = relationship("Book", back_populates="loans")
    reader = relationship("Reader", back_populates="loans")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    mensagem = Column(Text, nullable=False)
    tipo = Column(String(50), nullable=False)
    lida = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class BackupRecord(Base):
    __tablename__ = "backup_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
