// ===================================================
// Variables globales y configuración inicial
// ===================================================
let history = [];
let userName = '';
let mediaRecorder;
let audioChunks = [];
let recognition;
let isListening = false;

// ===================================================
// Funciones de inicialización y manejo de conversación
// ===================================================

// Inicia la conversación al cargar la página
async function startConversation() {
    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: 'Inicia la conversación', history, name: userName })
        });
        const data = await response.json();
        if (data.reply) {
            appendMessage(data.reply, 'bot');
            history.push({ role: 'assistant', content: data.reply });
        }
    } catch (error) {
        console.error('Error al iniciar la conversación:', error);
    }
};

// Envía un mensaje de texto
async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();

    if (message) {
        // Si se detecta un comando de reinicio, se limpia el chat
        if (["terminar", "adiós", "fin", "chau"].includes(message.toLowerCase())) {
            history = [];
            userName = '';
            document.getElementById('chat-box').innerHTML = ''; // Limpiar el área del chat
        } else {
            history.push({ role: 'user', content: message });
            appendMessage(message, 'user');
        }
        input.value = '';

        try {
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, history, name: userName })
            });
            const data = await response.json();
            if (data.reply) {
                // Si se reinició, se limpia de nuevo el chat antes de agregar la respuesta
                if (["terminar", "adiós", "fin", "chau"].includes(message.toLowerCase())) {
                    document.getElementById('chat-box').innerHTML = '';
                }
                history.push({ role: 'assistant', content: data.reply });
                appendMessage(data.reply, 'bot');
            }
            // Actualiza el nombre del usuario si se detecta
            if (data.name) {
                userName = data.name;
            }
        } catch (error) {
            console.error('Error al enviar el mensaje:', error);
        }
    }
};

// Agrega un mensaje al área del chat
function appendMessage(message, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    messageElement.innerText = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
};

// ===================================================
// Funciones de manejo de grabación de audio
// ===================================================

// Inicia la grabación y muestra feedback visual
function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            audioChunks = [];

            // Feedback visual: indica que está grabando
            const statusElement = document.getElementById('record-status');
            if (statusElement) {
                statusElement.innerText = "Grabando...";
                statusElement.style.color = "red";
            }

            mediaRecorder.addEventListener("dataavailable", event => {
                audioChunks.push(event.data);
            });

            mediaRecorder.addEventListener("stop", () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                sendAudio(audioBlob);

                // Reiniciar feedback visual
                if (statusElement) {
                    statusElement.innerText = "";
                }
            });
        })
        .catch(err => {
            console.error("Error al acceder al micrófono:", err);
        });
};

// Detiene la grabación si está en curso
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
    }
};

// Envía el archivo de audio al endpoint /voice y procesa la respuesta
async function sendAudio(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'grabacion.wav');
    formData.append('history', JSON.stringify(history));
    formData.append('name', userName);

    try {
        const response = await fetch('/voice', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.transcription) {
            history.push({ role: 'user', content: data.transcription });
            appendMessage(data.transcription, 'user');
        }
        if (data.reply) {
            history.push({ role: 'assistant', content: data.reply });
            appendMessage(data.reply, 'bot');
        }
    } catch (error) {
        console.error("Error al enviar el audio:", error);
    }
}

// ===================================================
// Funciones de reconocimiento de voz
// ===================================================

function toggleSpeechRecognition() {
    // Verifica compatibilidad con la API
    if (!('webkitSpeechRecognition' in window)) {
        alert('Tu navegador no soporta el reconocimiento de voz.');
        return;
    }

    const micButton = document.getElementById('mic-button');

    if (!recognition) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'es-ES';

        recognition.onresult = (event) => {
            let transcript = event.results[0][0].transcript;
            // Convierte la primera letra a mayúscula
            transcript = transcript.charAt(0).toUpperCase() + transcript.slice(1);
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
        isListening = false;
        micButton.classList.remove("recording");
    } else {
        recognition.start();
        isListening = true;
        micButton.classList.add("recording");
    }
}

// ===================================================
// Event Listeners y ejecución al cargar la página
// ===================================================

// Enviar mensaje al presionar Enter
document.getElementById('message-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Iniciar conversación al cargar la página
window.onload = function () {
    startConversation();
};
