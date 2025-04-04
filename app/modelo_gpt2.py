from dotenv import load_dotenv
from flask import render_template, request, Blueprint, current_app

from flask import Blueprint, request, render_template, current_app

gpt2_blueprint = Blueprint("gpt2", __name__)

@gpt2_blueprint.route("/", methods=["GET", "POST"])
def index():
    receta = ""
    tokenizer = current_app.config['TOKENIZER']
    model = current_app.config['MODEL']

    if request.method == "POST":
        ingredientes = request.form.get("ingredients", "").split(",")
        ingredientes = [i.strip() for i in ingredientes if i.strip()]

        if ingredientes:
            texto_entrada = f"Ingredientes: {', '.join(ingredientes)}\n\nReceta:"
            inputs = tokenizer(texto_entrada, return_tensors="pt", padding=True, truncation=True, max_length=512)

            outputs = model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=300,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.95,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.2,
            )

            receta = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return render_template("gpt2.html", receta=receta)
