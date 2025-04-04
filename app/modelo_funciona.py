from flask import Flask, render_template, request
from transformers import GPT2Tokenizer, GPT2LMHeadModel

app = Flask(__name__)

# Ruta donde guardaste el modelo entrenado
model_path = "modelos/gpt2"

# Cargar el tokenizador y el modelo
tokenizer = GPT2Tokenizer.from_pretrained(model_path)
model = GPT2LMHeadModel.from_pretrained(model_path)

# Configurar token de padding
tokenizer.pad_token = tokenizer.eos_token

@app.route("/", methods=["GET", "POST"])
def index():
    receta = ""
    if request.method == "POST":
        # Obtener los ingredientes del formulario
        ingredientes = request.form.get("ingredients").split(",")
        ingredientes = [i.strip() for i in ingredientes]

        # Crear la entrada a partir de los ingredientes
        texto_entrada = f"Ingredientes: {', '.join(ingredientes)}\n\nReceta:"

        # Tokenizar entrada
        inputs = tokenizer(texto_entrada, return_tensors="pt", padding=True, truncation=True, max_length=512)

        # Generar texto con el modelo
        outputs = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=300,              # Longitud máxima del texto generado
            num_return_sequences=1,      # Generar solo una receta
            temperature=0.7,             # Ajustar creatividad
            top_p=0.95,                  # Usar muestreo de núcleo
            do_sample=True,              # Activar el muestreo
            pad_token_id=tokenizer.eos_token_id,  # Usar EOS como token de padding
            repetition_penalty=1.2,      # Penalizar repeticiones
        )

        # Decodificar la receta generada
        receta = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return render_template("index.html", receta=receta)

if __name__ == "__main__":
    app.run(debug=True)
