# app/__init__.py

import os

from dotenv import load_dotenv
from flask import Flask
from transformers import GPT2LMHeadModel, GPT2Tokenizer

from .imagen import imagen_blueprint  # Importar blueprint de imagen
from .modelo_gpt2 import gpt2_blueprint  # Importar blueprint de imagen

# Cargar variables de entorno desde el archivo .env (si lo usas)
load_dotenv()

# Obtener la ruta del directorio actual (donde está app)
basedir = os.path.abspath(os.path.dirname(__file__))

# Crear la instancia de la aplicación Flask
app = Flask(__name__)

# Obtener la ruta del modelo
model_path = os.getenv("ruta_gpt2")

# Cargar modelo y tokenizador
tokenizer = GPT2Tokenizer.from_pretrained(model_path, local_files_only=True)
model = GPT2LMHeadModel.from_pretrained(model_path, local_files_only=True)

# Guardar en app.config para evitar problemas de importación circular
app.config["tokenizer"] = tokenizer
app.config["model"] = model
app.register_blueprint(imagen_blueprint, url_prefix="/select-ingredients")
app.register_blueprint(gpt2_blueprint, url_prefix="/gpt2")
# Importar los routers para que se registren las rutas
from app import routes
