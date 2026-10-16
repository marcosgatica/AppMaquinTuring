import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Configurar el motor de conexión
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definir el modelo de la tabla
class HistorialTuring(Base):
    __tablename__ = "historial_turing"

    id = Column(Integer, primary_key=True, index=True)
    cadena_entrada = Column(String(50), nullable=False)
    alfabeto = Column(String(100), nullable=False)
    nodos_configurados = Column(Integer, nullable=False)
    metodo = Column(String(50), nullable=False)
    cinta_resultante = Column(String(50))
    estado_final = Column(String(20))
    # ¡PostgreSQL guarda JSON de forma nativa! Perfecto para las transiciones
    log_transiciones = Column(JSON) 
    fecha_analisis = Column(DateTime, default=datetime.utcnow)

# Instrucción para que SQLAlchemy cree la tabla en Postgres si no existe
Base.metadata.create_all(bind=engine)