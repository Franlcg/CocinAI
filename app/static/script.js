// ===================================================
// Variables globales y configuración inicial
// ===================================================
let mediaRecorder;
let audioChunks = [];
let recognition;
let isListening = false;
let processingMessageId = null;
let processingTimeout = null;

// ===================================================
// Inicialización de la conversación al cargar la página
// ===================================================
async function startConversation() {
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ iniciar_conversacion: true })
        });
        const data = await response.json();

        if (data.reply) {
            appendMessage(data.reply, 'bot');
        }
    } catch (error) {
        console.error('Error al iniciar la conversación:', error);
    }
}

// ===================================================
// Enviar mensaje de texto
// ===================================================
async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();

    if (message) {
        appendMessage(message, 'user');
        input.value = '';

        if (["nada más", "eso es todo", "no"].includes(message.toLowerCase())) {
            showProcessingMessage();
        }

        try {
            const minProcessingTime = new Promise(resolve => {
                processingTimeout = setTimeout(resolve, 2000);
            });

            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            await minProcessingTime;
            removeProcessingMessage();

            if (data.reply && !data.receta) {
                // Solo mostrar en el chat si NO es una receta
                appendMessage(data.reply, 'bot');
            }

            if (data.name) {
                updateUserUI(data.name);
            }

            if (data.ingredients) {
                updateIngredientsUI(data.ingredients);
            }

            if (data.receta) {
                // Mostrar receta solo en la sección de receta sugerida
                document.getElementById('recipe-result').innerText = data.receta;
            }

        } catch (error) {
            console.error('Error al enviar el mensaje:', error);
            removeProcessingMessage();
        }
    }
}


// ===================================================
// Mostrar/eliminar mensaje de "procesando..."
// ===================================================
function showProcessingMessage() {
    if (processingMessageId) return;

    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', 'bot', 'processing');
    messageElement.innerText = 'Procesando...';
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;

    processingMessageId = messageElement;
}

function removeProcessingMessage() {
    if (processingMessageId) {
        processingMessageId.remove();
        processingMessageId = null;
    }

    if (processingTimeout) {
        clearTimeout(processingTimeout);
        processingTimeout = null;
    }
}

// ===================================================
// Añadir mensaje al chat
// ===================================================
function appendMessage(message, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    messageElement.innerText = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ===================================================
// Actualizar la lista de ingredientes
// ===================================================
function updateIngredientsUI(ingredients) {
    const ingredientsList = document.getElementById('ingredients-list');
    ingredientsList.innerHTML = ''; // Limpiar lista anterior

    ingredients.forEach(ingredient => {
        const ingredientElement = document.createElement('div');
        ingredientElement.classList.add('ingredient');
        ingredientElement.textContent = ingredient;
        ingredientsList.appendChild(ingredientElement);
    });
}

// ===================================================
// Manejo de audio
// ===================================================
async function sendAudio(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'grabacion.wav');

    try {
        showProcessingMessage();
        const minProcessingTime = new Promise(resolve => {
            processingTimeout = setTimeout(resolve, 2000);
        });

        const response = await fetch('/voice', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        await minProcessingTime;
        removeProcessingMessage();

        if (data.transcription) {
            appendMessage(data.transcription, 'user');
        }
        if (data.reply) {
            appendMessage(data.reply, 'bot');
        }

        if (data.name) updateUserUI(data.name);

        if (data.ingredients) updateIngredientsUI(data.ingredients);

    } catch (error) {
        console.error("Error al enviar el audio:", error);
    }
}

// ===================================================
// Reconocimiento de voz
// ===================================================
function toggleSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        alert('Tu navegador no soporta reconocimiento de voz.');
        return;
    }

    const micButton = document.getElementById('mic-button');

    if (!recognition) {
        recognition = new webkitSpeechRecognition();
        recognition.lang = 'es-ES';

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            document.getElementById('message-input').value = transcript;
            sendMessage();
        };

        recognition.onend = () => {
            isListening = false;
            micButton.classList.remove("recording");
        };
    }

    if (isListening) {
        recognition.stop();
        micButton.classList.remove("recording");
        isListening = false;
    } else {
        recognition.start();
        micButton.classList.add("recording");
        isListening = true;
    }
}

// ===================================================
// Actualizar interfaz de usuario
// ===================================================
function updateUserUI(name) {
    const nameDisplay = document.getElementById('username-display');
    if (name) {
        nameDisplay.style.opacity = 0;
        setTimeout(() => {
            nameDisplay.textContent = name;
            nameDisplay.style.opacity = 1;
        }, 500);
    }
}

// ===================================================
// Eventos
// ===================================================
document.getElementById('message-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

window.onload = startConversation;
