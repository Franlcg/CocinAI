import os
import torch
from flask import Blueprint, request, render_template
from transformers import GPT2Tokenizer, GPT2LMHeadModel

gpt2_blueprint = Blueprint("gpt2", __name__)
# Obtener la ruta del modelo
model_path = os.getenv("RUTA_GPT2")

# Detectar si CUDA está disponible y establecer el dispositivo
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Cargar modelo y tokenizador
tokenizer = GPT2Tokenizer.from_pretrained(model_path, local_files_only=True)
model = GPT2LMHeadModel.from_pretrained(model_path, local_files_only=True).to(device)


@gpt2_blueprint.route("/", methods=["GET", "POST"])
def index():
    """
    Maneja solicitudes GET y POST para generar recetas con GPT-2.

    GET: Muestra el formulario para ingresar ingredientes.
    POST: Genera una receta a partir de los ingredientes ingresados.

    Returns:
        str: HTML renderizado con la receta generada o mensaje de error.
    """

    receta_generada = ""
    # Obtener tokenizer y modelo del objeto Flask actual
    # Recuperar el tokenizer y modelo cargados en la app Flask

    if not tokenizer or not model:
        return "Error: El modelo o el tokenizer no están disponibles.", 500

    if request.method == "POST":
        # Obtener ingredientes desde el formulario
        ingredientes_raw = request.form.get("ingredients", "")
        ingredientes = [i.strip() for i in ingredientes_raw.split(",") if i.strip()]

        if ingredientes:
            texto_entrada = f"Ingredientes seleccionados: {', '.join(ingredientes)}\n\nReceta:"

            try:
                inputs = tokenizer(
                    texto_entrada,
                    return_tensors="pt",    # Usamos tensores para PyTorch
                    padding=True,           # Rellenamos si es necesario
                    truncation=True,        # Cortamos si es muy largo
                    max_length=512          # Límite de longitud de entrada
                )

                # Mover los tensores al mismo dispositivo que el modelo
                inputs = {key: val.to(device) for key, val in inputs.items()}

                outputs = model.generate(
                    input_ids=inputs["input_ids"],              # IDs de entrada del texto
                    attention_mask=inputs["attention_mask"],    # Máscara que indica qué partes del texto son reales y cuáles son relleno
                    max_length=300,                             # Máximo de palabras generadas
                    num_return_sequences=1,                     # Solo una receta
                    temperature=0.7,                            # Variedad en el texto 0.1 - 2.0
                    top_p=0.95,                                 # Filtrado para creatividad 0.0 – 1.0
                    do_sample=True,                             # Generación aleatoria
                    pad_token_id=tokenizer.eos_token_id,        # ID para rellenar si falta espacio
                    repetition_penalty=1.2,                     # Penaliza repeticiones 1.0 - 2.0
                )

                receta_generada = tokenizer.decode(outputs[0], skip_special_tokens=True)

            except Exception as e:
                return f"Error al generar la receta: {str(e)}", 500

    return render_template("gpt2.html", receta=receta_generada)
