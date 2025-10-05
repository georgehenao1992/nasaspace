# OA Híbrido: Gemini + GPT + Avatar Animado (Mac-safe)

OA Híbrido es un asistente empático con avatar animado, que combina inteligencia artificial de **Google Gemini** y **OpenAI GPT**, detecta emociones en tiempo real mediante cámara, y responde por voz usando **gTTS**. El proyecto está optimizado para **Mac** y utiliza **Tkinter** para mostrar un avatar animado.

---

## Funcionalidades

- Detecta emociones del usuario usando **DeepFace**.
- Analiza el rostro y determina la emoción dominante (feliz, triste, enojado, neutral, asustado, sorprendido, disgustado).
- Conversación empática en español mediante **GPT-4o-mini** y respuestas adaptadas a la emoción detectada.
- Avatar animado en **Tkinter** que cambia según el estado “hablando” o reposo.
- Entrada y salida de voz mediante **SpeechRecognition** y **gTTS**.
- Visualización de la cámara con overlay de análisis emocional usando **OpenCV**.

---

## Requisitos

Instalar dependencias con pip:

```bash
pip install -r requirements.txt
