# run.py
from app import app  # Se importa la instancia de la aplicación Flask desde la carpeta app

if __name__ == '__main__':
    # Ejecuta la aplicación en modo debug (solo para desarrollo)
    app.run(debug=False)
