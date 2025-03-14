# app/routers.py

import io
import os
import json
import traceback
from flask import request, jsonify, render_template
import openai
from app import app

# Configuración de la API de OpenAI: se obtiene la clave desde las variables de entorno.
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    """
    Renderiza la página principal del chatbot.
    """
    print("Rutas de búsqueda de plantillas:", app.jinja_loader.searchpath)
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    """
    Procesa los mensajes enviados desde el cliente y se comunica con OpenAI para generar una respuesta.
    """
    data = request.get_json()
    user_message = data.get('message')
    history = data.get('history', [])
    user_name = data.get('name', '')

    if not user_message:
        return jsonify({'error': 'Mensaje vacío'}), 400

    chatbot_name = "Asistente"

    # Si se detecta un comando de reinicio, se borra el historial y se retorna un mensaje fijo.
    if user_message.lower() in ['terminar', 'adiós', 'fin', 'chau']:
        history = []
        user_name = ''
        return jsonify({'reply': "¡Hola! Soy Asistente. ¿Cómo te llamas?", 'name': user_name})

    try:
        if user_message.lower() == "inicia la conversación":
            history.append({
                "role": "system",
                "content": (
                    f"Eres {chatbot_name}, un asistente amigable que siempre responde en español. "
                    "Saluda al usuario y pregúntale cómo se llama. Si el usuario te dice su nombre, recuérdalo y úsalo en las respuestas futuras. "
                    f"No cambies tu nombre; siempre eres {chatbot_name}. Responde SIEMPRE en español, incluso si el usuario habla en otro idioma."
                )
            })
            user_message = "Hola"

        if user_name:
            history.insert(0, {
                "role": "system",
                "content": (
                    f"El nombre del usuario es {user_name}. Responde siempre en español de manera amigable. "
                    f"Tu nombre es {chatbot_name}. No cambies tu nombre y usa el nombre del usuario en las respuestas si es necesario. "
                    "Responde SIEMPRE en español."
                )
            })

        history.append({
            "role": "user",
            "content": user_message
        })

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history
        )

        reply = response.choices[0].message.content

        # Si el usuario indica su nombre en el mensaje, se extrae y se actualiza la variable user_name.
        if "mi nombre es" in user_message.lower():
            detected_name = user_message.split("mi nombre es")[-1].strip().capitalize()
            if detected_name.lower() != chatbot_name.lower():
                user_name = detected_name

        return jsonify({'reply': reply, 'name': user_name})
    except Exception as e:
        print("Error en /ask:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/voice', methods=['POST'])
def voice():
    """
    Procesa el archivo de audio enviado desde el cliente, realiza la transcripción y genera una respuesta.
    """
    if 'audio' not in request.files:
        return jsonify({'error': 'No se ha subido ningún archivo de audio'}), 400

    audio_file = request.files['audio']
    audio_bytes = audio_file.read()
    audio_stream = io.BytesIO(audio_bytes)
    audio_stream.name = audio_file.filename

    history_str = request.form.get('history', '[]')
    user_name = request.form.get('name', '')
    chatbot_name = "Asistente"

    try:
        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_stream,
            language="es"
        )
        user_message = transcription.text
    except Exception as e:
        print("Error en transcripción:")
        traceback.print_exc()
        return jsonify({'error': f'Error en la transcripción: {str(e)}'}), 500

    try:
        history = json.loads(history_str)
    except Exception:
        history = []

    history.append({"role": "user", "content": user_message})
    if user_name:
        history.insert(0, {
            "role": "system",
            "content": (
                f"El nombre del usuario es {user_name}. Responde siempre en español de manera amigable. "
                f"Tu nombre es {chatbot_name}. No cambies tu nombre y usa el nombre del usuario en las respuestas si es necesario. "
                "Responde SIEMPRE en español."
            )
        })

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history
        )
        reply = response.choices[0].message.content
    except Exception as e:
        print("Error en generación de respuesta:")
        traceback.print_exc()
        return jsonify({'error': f'Error en la generación de respuesta: {str(e)}'}), 500

    return jsonify({'transcription': user_message, 'reply': reply})
