import io
import os
import json
import traceback
from flask import Flask, request, jsonify, render_template, session
import openai
from app import app

# Clave secreta para sesiones
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Configuración de OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")


# Simulación de función de red neuronal para generar receta
def generar_receta(nombre, ingredientes):
    try:
        prompt = (
            f"Hola, mi nombre es {nombre}. Tengo estos ingredientes: {', '.join(ingredientes)}.\n"
            "Por favor, crea una receta detallada y en español que pueda preparar usando solo esos ingredientes. "
            "Incluye un título, lista de pasos y sugerencias si faltan ingredientes comunes."
        )

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "Eres un chef experto que genera recetas en español basadas en los ingredientes disponibles del usuario. "
                    "Sé claro, ordenado y amigable. Incluye título y pasos numerados."
                )},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=600,
            top_p=0.9
        )

        receta_generada = response.choices[0].message.content.strip()
        return receta_generada

    except Exception as e:
        traceback.print_exc()
        return "Hubo un error generando la receta con OpenAI."



# Ruta página principal (get)
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat')
def chat():
    return render_template('chat.html')


# Ruta ask para el envío de información (POST)
@app.route('/ask', methods=['POST'])
def ask():
    # Nombre del chatbot
    chatbot_name = "CocinAI"
    # Datos recibidos por POST
    data = request.get_json()
    # Obtener de data message
    user_message = data.get('message', '')
    # Obtener de data iniciar_conversación
    iniciar_conversacion = data.get('iniciar_conversacion', False)
    # Obtenemos de sesión user_name si estuviera
    user_name = session.get('user_name', '')
    # Obtenemos de sesión ingredientes si estuviera
    ingredientes = session.get('ingredientes', [])
    # Obtenemos de sesión el historial si estuviera
    history = session.get('history', [])

    # Si se inicia la conversación, borramos sesión y añadimos este prompt al  historial
    if iniciar_conversacion:
        session.clear()
        session['history'] = [
            {"role": "system", "content": (
                f"Eres {chatbot_name}, un asistente amigable que ayuda al usuario a preparar recetas basadas en los ingredientes que mencione. "
                "Responde SIEMPRE en español. Usa lenguaje claro, directo y amigable. "
                f"Tu nombre es siempre {chatbot_name}. Solicita primero el nombre del usuario."
            )}
        ]
        # Hacemos la primera pregunta al usuario
        return jsonify({'reply': f"¡Hola! Soy {chatbot_name}. ¿Cómo te llamas?"})
    # Si estuviera vacío el mensaje mostramos el error
    if not user_message:
        return jsonify({'error': 'Mensaje vacío'}), 400
    # Agregamos al historial el prompt
    history.append({"role": "user", "content": user_message})

    # 1. Detectar nombre (si aún no lo tenemos)
    if not user_name:
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": user_message},
                    {"role": "system", "content": (
                        "Si detectas un nombre en el mensaje responde SOLO en formato JSON sin texto adicional: "
                        "{\"nombre_detectado\": true, \"nombre\": \"Nombre\"} "
                        "Si no detectas nombre: {\"nombre_detectado\": false, \"nombre\": null}"
                    )}
                ]
            )
            respuesta_nombre = response.choices[0].message.content.strip()
            datos_nombre = json.loads(respuesta_nombre)

            if datos_nombre.get('nombre_detectado'):
                user_name = datos_nombre['nombre']
                session['user_name'] = user_name
                return jsonify(
                    {'reply': f"¡Encantado {user_name}! ¿Qué ingredientes tienes disponibles?", 'name': user_name})

        except Exception as e:
            traceback.print_exc()
            return jsonify({'reply': "Disculpa, hubo un error detectando tu nombre. ¿Podrías repetirlo?"}), 500

    # 2. Detectar finalización (si usuario ya tiene nombre)
    try:
        response_finalizar = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_message},
                {"role": "system", "content": (
                    "Si el usuario no quiere añadir más ingredientes responde SOLO en formato JSON: "
                    "{\"finalizar\": true}. Si quiere continuar: {\"finalizar\": false}. "
                    "No incluyas texto adicional."
                )}
            ]
        )
        respuesta_finalizar = response_finalizar.choices[0].message.content.strip()
        datos_finalizar = json.loads(respuesta_finalizar)

        if datos_finalizar.get('finalizar'):
            receta = generar_receta(user_name, ingredientes)
            session.clear()
            return jsonify({
                'reply': receta,
                'name': user_name,
                'receta': receta,
                'finalizado': True
            })

    except Exception as e:
        traceback.print_exc()

    # 3. Detectar ingredientes (si no ha finalizado)
    try:
        response_ingredientes = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": user_message},
                {"role": "system", "content": (
                    "Detecta ingredientes mencionados por el usuario. Responde SOLO en formato JSON: "
                    "{\"ingredientes_detectados\": true, \"ingredientes\": [\"ingrediente1\", \"ingrediente2\"]}. "
                    "Si no detectas ingredientes: {\"ingredientes_detectados\": false, \"ingredientes\": []}. "
                    "No incluyas texto adicional."
                )}
            ]
        )
        respuesta_ingredientes = response_ingredientes.choices[0].message.content.strip()
        datos_ingredientes = json.loads(respuesta_ingredientes)

        if datos_ingredientes.get('ingredientes_detectados'):
            nuevos_ingredientes = datos_ingredientes['ingredientes']
            ingredientes = list(set(ingredientes + nuevos_ingredientes))
            session['ingredientes'] = ingredientes

            return jsonify({
                'reply': f"He detectado los siguientes ingredientes: {', '.join(ingredientes)}. ¿Algún ingrediente más?",
                'name': user_name,
                'ingredients': ingredientes,
                'finalizado': False
            })

        # Si no detecta ingredientes ni finalización
        return jsonify({
            'reply': "No entendí claramente. ¿Podrías indicarme los ingredientes o decirme si has terminado?",
            'name': user_name,
            'finalizado': False
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'reply': "Hubo un error detectando ingredientes. Intenta nuevamente."}), 500


# Ruta para enviar por voz (POST)
@app.route('/voice', methods=['POST'])
def voice():
    if 'audio' not in request.files:
        return jsonify({'error': 'No se ha subido audio'}), 400

    audio_file = request.files['audio']
    audio_bytes = audio_file.read()
    audio_stream = io.BytesIO(audio_bytes)
    audio_stream.name = audio_file.filename

    user_name = session.get('user_name', '')
    chatbot_name = "CocinAI"

    try:
        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_stream,
            language="es"
        )
        user_message = transcription.text
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Error en la transcripción'}), 500

    return jsonify({'transcription': user_message})
