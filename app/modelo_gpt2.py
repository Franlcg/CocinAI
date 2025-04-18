import os

from flask import Blueprint, request, render_template
from transformers import GPT2Tokenizer, GPT2LMHeadModel

gpt2_blueprint = Blueprint("gpt2", __name__)
# Obtener la ruta del modelo
model_path = os.getenv("ruta_gpt2")

# Cargar modelo y tokenizador
tokenizer = GPT2Tokenizer.from_pretrained(model_path, local_files_only=True)
model = GPT2LMHeadModel.from_pretrained(model_path, local_files_only=True)


@gpt2_blueprint.route("/", methods=["GET", "POST"])
def index():
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
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                )

                outputs = model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_length=300,
                    num_return_sequences=1,
                    temperature=0.7,
                    top_p=0.95,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    repetition_penalty=1.2,
                )

                receta_generada = tokenizer.decode(outputs[0], skip_special_tokens=True)

            except Exception as e:
                return f"Error al generar la receta: {str(e)}", 500

    return render_template("gpt2.html", receta=receta_generada)
