import os
import string
import requests
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, request, render_template

# Cargar variables de entorno desde el archivo .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Verificar si la clave de API se ha cargado correctamente
if openai.api_key is None:
    raise ValueError("No se pudo cargar la clave de API de OpenAI. Verifica tu archivo .env.")

# Crear aplicación Flask
app = Flask(__name__)


def extraer_ingredientes(url):
    """Extrae una lista de ingredientes y sus imágenes desde la URL proporcionada.

    Args:
        url (str): URL de la página web a extraer los ingredientes.

    Returns:
        dict: Diccionario con nombres de ingredientes como claves y URLs de imágenes como valores.
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        response.encoding = response.apparent_encoding  # Asegurar la correcta detección de la codificación
    except requests.RequestException as e:
        print(f"Error al acceder a la página {url}: {e}")
        return {}

    ingredientes = {}
    soup = BeautifulSoup(response.text, 'html.parser')  # Usar response.text en lugar de response.content

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



# Almacenar todos los ingredientes
def obtener_ingredientes_totales():
    """Obtiene un conjunto de ingredientes desde varias páginas y los devuelve como una lista de diccionarios.

    Returns:
        list: Lista de diccionarios con nombres de ingredientes y sus imágenes.
    """
    ingredientes_totales = {}

    # Recorre las primeras 5 letras del alfabeto (A-E) para obtener ingredientes
    for letra in string.ascii_uppercase[:27]:  # Limitar a 5 letras para prueba
        base_url = f'https://www.recetas.com/ingredientes/{letra}/'

        # Extraer de las primeras 2 páginas de cada letra
        for pagina in range(1, 3):
            url = base_url if pagina == 1 else f'{base_url}{pagina}/'
            ingredientes = extraer_ingredientes(url)
            ingredientes_totales.update(ingredientes)

    return [{"nombre": k, "imagen": v} for k, v in ingredientes_totales.items()]


# Página principal
@app.route("/", methods=["GET", "POST"])
def index():
    """Maneja la página principal donde se listan los ingredientes y se genera la receta.

    Returns:
        str: Renderiza la plantilla HTML con la lista de ingredientes y la receta generada.
    """
    ingredientes = obtener_ingredientes_totales()
    receta = None

    # Si el usuario envía el formulario, generar receta con los ingredientes seleccionados
    if request.method == "POST":
        seleccionados = request.form.getlist("ingredientes")
        if seleccionados:
            receta = generar_receta(", ".join(seleccionados))

    return render_template("select_ingredients.html", receta=receta, ingredientes=ingredientes)


# Función para generar receta con OpenAI
def generar_receta(ingredientes):
    """Genera una receta utilizando la API de OpenAI basándose en los ingredientes seleccionados.

    Args:
        ingredientes (str): Lista de ingredientes seleccionados en formato de cadena.

    Returns:
        str: Receta generada por OpenAI o un mensaje de error si la API falla.
    """
    prompt = f"Genera una receta con estos ingredientes: {ingredientes}."
    try:
        client = openai.OpenAI()
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


if __name__ == "__main__":
#   Descarga Las imagenes
#    ingredientes = obtener_ingredientes_totales()
#    diccionario_ingredientes = {item["nombre"]: item["imagen"] for item in ingredientes}
#    descargar_imagenes(diccionario_ingredientes)

    # Inicia la aplicación Flask en modo depuración
    app.run(debug=True)

