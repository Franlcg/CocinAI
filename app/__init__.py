# app/__init__.py

from flask import Flask
from dotenv import load_dotenv
import os
from .imagen import imagen_blueprint  # Importar blueprint de imagen
from .modelo_gpt2 import gpt2_blueprint  # Importar blueprint de imagen

# Cargar variables de entorno desde el archivo .env (si lo usas)
load_dotenv()

# Obtener la ruta del directorio actual (donde está app)
basedir = os.path.abspath(os.path.dirname(__file__))

# Crear la instancia de la aplicación Flask
app = Flask(__name__)
app.register_blueprint(imagen_blueprint, url_prefix="/select-ingredients")
app.register_blueprint(gpt2_blueprint, url_prefix="/gpt2")
# Importar los routers para que se registren las rutas
from app import routes
