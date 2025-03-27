# app/__init__.py

from flask import Flask
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env (si lo usas)
load_dotenv()

# Obtener la ruta del directorio actual (donde está app)
basedir = os.path.abspath(os.path.dirname(__file__))

# Crear la instancia de la aplicación Flask
app = Flask(__name__)

# Importar los routers para que se registren las rutas
from app import routes
from app import imagen
