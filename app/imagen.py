import os

import openai
import requests
from bs4 import BeautifulSoup
from flask import request, render_template, Blueprint
from flask.cli import load_dotenv

load_dotenv()
# Crear el blueprint de imagen
imagen_blueprint = Blueprint('imagen', __name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

# Verificar si la clave de API se ha cargado correctamente
if openai.api_key is None:
    raise ValueError("No se pudo cargar la clave de API de OpenAI. Verifica tu archivo .env.")


def extraer_ingredientes(url):
    """
    Extrae una lista de ingredientes y sus imágenes desde la URL proporcionada.

    Args:
        url (str): URL de la página web de donde se extraerán los ingredientes.

    Returns:
        dict: Diccionario con nombres de ingredientes como claves y URLs de imágenes como valores.
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        response.encoding = "utf-8"  # Asegurar la correcta detección de la codificación
    except requests.RequestException as e:
        print(f"Error al acceder a la página {url}: {e}")
        return {}

    ingredientes = {}
    soup = BeautifulSoup(response.text, 'html.parser')  # Usar response.text en lugar de response.content

    # Buscar todos los enlaces con el atributo 'title' que contengan ingredientes
    for link in soup.find_all('a', title=True):
        nombre = link['title'].strip()
        # Si el nombre empieza con "Receta", se ignora
        if nombre.lower().startswith("receta"):
            continue

        img_tag = link.find('img')
        img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else ''

        if nombre and img_url:
            ingredientes[nombre] = img_url

    if not ingredientes:
        print(f"No se encontraron ingredientes en {url}. Verifica la estructura HTML.")

    return ingredientes


def obtener_ingredientes_totales():
    """
     Recolecta y ordena alfabéticamente ingredientes desde una página web.

    Returns:
        list: Lista ordenada de diccionarios, cada uno con el nombre y la imagen de un ingrediente.

    """
    ingredientes_totales = {}

    base_url = f'https://www.recetas.com/ingredientes/'

    # Recorre las páginas
    for pagina in range(0, 15):
        url = base_url if pagina == 1 else f'{base_url}{pagina}/'
        ingredientes = extraer_ingredientes(url)
        ingredientes_totales.update(ingredientes)

    # Crea una lista de diccionarios ordenada alfabéticamente por el nombre
    lista_ordenada = sorted(
        [{"nombre": k, "imagen": v} for k, v in ingredientes_totales.items()],
        key=lambda x: x["nombre"].lower()  # para ordenar sin distinguir mayúsculas/minúsculas
    )
    return lista_ordenada


def generar_receta(ingredientes):
    """
    Genera una receta utilizando la API de OpenAI basándose en los ingredientes seleccionados.

    Args:
        ingredientes (str): Lista de ingredientes seleccionados en formato de cadena.

    Returns:
        str: Receta generada por OpenAI o un mensaje de error si la API falla.
    """
    prompt = f"Genera una receta con estos ingredientes: {ingredientes}."
    try:
        client = openai.OpenAI()  # Se usa un cliente en la nueva API
        respuesta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return respuesta.choices[0].message.content
    except Exception as e:
        return f"Error al generar receta: {str(e)}"


def descargar_imagenes(ingredientes, carpeta="static/imagenes/ingredientes"):
    """Descarga imágenes de ingredientes y las guarda con su nombre.

    Args:
        ingredientes (dict): Diccionario con nombres de ingredientes como claves y URLs de imágenes como valores.
        carpeta (str): Carpeta donde se guardarán las imágenes.
    """
    # Crear la carpeta si no existe
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    for nombre, url in ingredientes.items():
        try:
            # Reemplazar caracteres no permitidos en nombres de archivo
            nombre_archivo = "".join(c for c in nombre if c.isalnum() or c in (" ", "-")).rstrip()
            ruta_archivo = os.path.join(carpeta, f"{nombre_archivo}.jpg")

            # Descargar la imagen
            response = requests.get(url, stream=True, timeout=5)
            response.raise_for_status()  # Lanza un error si la descarga falla

            # Guardar la imagen
            with open(ruta_archivo, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

            print(f" Imagen guardada: {ruta_archivo}")

        except requests.RequestException as e:
            print(f" Error al descargar {nombre}: {e}")


@imagen_blueprint.route("/", methods=["GET", "POST"], )
def select_ingredients():
    """
    Maneja la página de selección de ingredientes y generación de recetas.

    Returns:
        str: Página HTML con la lista de ingredientes y la receta generada (si aplica).
    """
    receta = None
    seleccionados = []

    # Si el usuario envía el formulario, generar receta con los ingredientes seleccionados
    if request.method == "POST":
        seleccionados = request.form.getlist("ingredientes")
        if seleccionados:
            receta = generar_receta(", ".join(seleccionados))

    return render_template("select_ingredients.html", receta=receta, ingredientes=obtener_ingredientes_totales(),
                           seleccionados=seleccionados)

# if __name__ == "__main__":
#     #   Descarga Las imagenes
#     #    ingredientes = obtener_ingredientes_totales()
#     #    diccionario_ingredientes = {item["nombre"]: item["imagen"] for item in ingredientes}
#     #    descargar_imagenes(diccionario_ingredientes)
#
#     # Inicia la aplicación Flask en modo depuración
#     app.run(debug=True)
