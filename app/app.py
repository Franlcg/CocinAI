import os
import openai
from flask import Flask, request, render_template
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Verificar si la clave de API se ha cargado correctamente
if openai.api_key is None:
    raise ValueError("No se pudo cargar la clave de API de OpenAI. Asegúrate de que el archivo .env esté configurado correctamente.")

# Crear la aplicación Flask
app = Flask(__name__)

# Lista de ingredientes con imágenes de Wikipedia
INGREDIENTES = [
    {"nombre": "Tomate", "imagen": "https://upload.wikimedia.org/wikipedia/commons/8/89/Tomato_je.jpg"},
    {"nombre": "Cebolla", "imagen": "https://upload.wikimedia.org/wikipedia/commons/1/1b/Onions.jpg"},
    {"nombre": "Pimiento", "imagen": "https://upload.wikimedia.org/wikipedia/commons/d/de/Capsicum_annuum_fruits_IMGP0049.jpg"},
    {"nombre": "Pollo", "imagen": "https://upload.wikimedia.org/wikipedia/commons/a/a5/Roast_chicken.jpg"},
    {"nombre": "Arroz", "imagen": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Arroz_Integral.jpg"},
    {"nombre": "Queso", "imagen": "https://upload.wikimedia.org/wikipedia/commons/4/45/Cheese.jpg"},
]

# Página principal con selección de ingredientes
@app.route("/", methods=["GET", "POST"])
def index():
    receta = None
    if request.method == "POST":
        ingredientes = request.form.getlist("ingredientes")  # Obtener ingredientes seleccionados
        if ingredientes:
            receta = generar_receta(", ".join(ingredientes))
    return render_template("index2.html", receta=receta, ingredientes=INGREDIENTES)

# Función para generar la receta usando OpenAI
def generar_receta(ingredientes):
    prompt = f"Genera una receta usando los siguientes ingredientes: {ingredientes}."

    try:
        client = openai.OpenAI()  # Se usa un cliente en la nueva API
        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error al generar receta: {str(e)}"

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True)

