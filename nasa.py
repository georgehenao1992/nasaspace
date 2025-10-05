# ====================================================
# OA HÍBRIDO: Gemini + GPT + AVATAR ANIMADO Holografia
# ====================================================
from deepface import DeepFace
import cv2
from collections import deque
import time
import google.generativeai as genai
from openai import OpenAI
from gtts import gTTS
import playsound
import speech_recognition as sr
import os
import threading
import tkinter as tk
from PIL import Image, ImageTk
import queue


# CONFIGURACIÓN DE APIs
genai.configure(api_key="AIzaSyCY75ZcCZ0_i40qJuE-koUO_Be43Qdk_tA")  # ⚠️ Usa tu clave de Google AI Studio
modelo = genai.GenerativeModel("models/gemini-2.5-flash")
client = OpenAI(api_key="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")


# VARIABLES GLOBALES
hablando = False
frames = []
etiqueta = None  
ventana = None
frame_queue = queue.Queue()  

# CARGAR AVATAR
def cargar_frames(master):
    global frames
    carpeta = "frames"
    for i in range(1, 51):
        ruta = os.path.join(carpeta, f"frame{i}.jpg")
        if os.path.exists(ruta):
            imagen = Image.open(ruta).resize((1600, 1000))
            frames.append(ImageTk.PhotoImage(imagen, master=master))
        else:
            print(f"⚠️ Imagen no encontrada: {ruta}")
    print(f"✅ {len(frames)} imágenes cargadas para animación.")


# ANIMACIÓN (hilo principal)
def actualizar_animacion():
    global hablando, frames, etiqueta
    if frames:
        if hablando:
            for frame in frames:
                etiqueta.config(image=frame)
                etiqueta.update()
                time.sleep(0.04)
        else:
            etiqueta.config(image=frames[0])
    ventana.after(100, actualizar_animacion)


# VOZ
r = sr.Recognizer()
mic = sr.Microphone()
with mic as source:
    print("🎛️ Calibrando micrófono...")
    r.adjust_for_ambient_noise(source, duration=1)
print("✅ Micrófono calibrado correctamente.")

def hablar(texto):
    global hablando
    print(f"\n🤖 OA: {texto}")
    tts = gTTS(text=texto, lang='es')
    archivo = "voz_temp.mp3"
    tts.save(archivo)
    hablando = True
    playsound.playsound(archivo)
    hablando = False
    os.remove(archivo)


# DETECCIÓN DE EMOCIÓN (hilo secundario)
def detectar_emocion():
    cap = cv2.VideoCapture(0)
    emotion_queue = deque(maxlen=10)
    rostro_detectado = False
    hablar("Sistema OA activado. Calibrando sensores visuales...")

    start = time.time()
    while not rostro_detectado and (time.time() - start) < 15:
        ret, frame = cap.read()
        if not ret:
            continue
        try:
            deteccion = DeepFace.detectFace(frame, enforce_detection=False)
            if deteccion is not None:
                rostro_detectado = True
                break
        except:
            continue

    if not rostro_detectado:
        hablar("No detecté rostro, continuaré con tono neutro.")
        cap.release()
        return "neutral"

    hablar("Rostro detectado. Analizando emoción...")

    traduccion = {
        "happy": "feliz",
        "sad": "triste",
        "angry": "enojado",
        "neutral": "neutral",
        "fear": "asustado",
        "surprise": "sorprendido",
        "disgust": "disgustado"
    }

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        try:
            result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            dominant = result[0]['dominant_emotion']
        except:
            dominant = "neutral"

        emotion_queue.append(dominant)

        # Enviar frame a la cola para mostrar en el hilo principal
        frame_queue.put(frame)

        # Revisar consistencia de emoción
        if len(emotion_queue) == emotion_queue.maxlen and len(set(emotion_queue)) == 1:
            emocion_es = traduccion.get(dominant, "neutral")
            hablar(f"Detecto que te sientes {emocion_es}.")
            cap.release()
            return dominant


# RESPUESTA EMOCIONAL
def respuesta_emocional(emocion):
    prompt = f"""
Eres OA, un asistente empático dentro de una nave espacial.
El rostro del usuario refleja la emoción: {emocion}.

        "sad": "La persona parece triste. Dile algo amable, motivador y empático en español.",
        "angry": "La persona está enojada. Usa un tono calmado y comprensivo para ayudar a tranquilizarla.",
        "happy": "La persona está feliz. Refuérzalo positivamente con entusiasmo.",
        "neutral": "La persona está tranquila. Haz una conversación amable y relajada.",
        "fear": "La persona parece asustada. Dale seguridad y calma.",
        "surprise": "La persona está sorprendida. Habla con curiosidad positiva."

Responde en máximo 3 líneas, de forma amable y reconfortante.
"""
    try:
        respuesta = modelo.generate_content(prompt)
        return respuesta.text.strip()
    except Exception as e:
        print("⚠️ Error con Gemini:", e)
        return "Hola, noto algo en ti, ¿cómo te sientes hoy?"


# RESPUESTA GPT
def generar_respuesta(pregunta, emocion):
    contexto = f"""
Eres OA, asistente técnico y empático de una nave espacial.
El usuario parece {emocion}.
Siempre respondes en español, con un tono calmado, técnico y empático.
Tus respuestas deben:
- Ser cortas (máximo 3 párrafos o 6 líneas).
- Terminar con una sugerencia práctica.
- No puedo comunicarme con un médico en tierra
- No se pueden realizar acciones de enjuague bucal, estás dentro de una nave espacial
- Sugerir conectar al médico en tierra.
- Evitar frases vagas o fuera del entorno espacial.
- Incluir solo recursos disponibles dentro de la nave (no hay tiendas, hospitales ni internet).
- Mostrar seguridad y serenidad, sin generar alarma.
- Si la situación es grave, pide calma y describe un procedimiento básico y seguro.

Ejemplo de cierre:
“Respira profundo, estamos a salvo y recuerda los protocolos de salud que ya las sabes, puedes contarme cómo es tu dolor”
Máximo 4 líneas por respuesta. No contactes con el exterior ni menciones internet.
"""
    mensajes = [
        {"role": "system", "content": contexto},
        {"role": "user", "content": pregunta}
    ]
    try:
        respuesta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=mensajes
        )
        return respuesta.choices[0].message.content.strip()
    except Exception as e:
        print("⚠️ Error con GPT:", e)
        return "Tuve una interferencia en el canal, ¿puedes repetir?"


# CONVERSACIÓN
def conversar(emocion):
    hablar("Estoy aquí para escucharte. Cuando termines, di 'gracias por tu ayuda'.")
    while True:
        try:
            print("🎧 Escuchando...")
            audio = r.listen(mic, timeout=6, phrase_time_limit=8)
            texto = r.recognize_google(audio, language="es-ES").lower()
            print(f"👤 Usuario: {texto}")

            if "gracias por tu ayuda" in texto or "salir" in texto:
                hablar("Ha sido un placer asistirte. Cerrando comunicación.")
                break

            respuesta = generar_respuesta(texto, emocion)
            hablar(respuesta)

        except sr.UnknownValueError:
            hablar("No te entendí, ¿podrías repetirlo?")
        except Exception as e:
            print("⚠️ Error general:", e)
            continue


# MAIN LOOP
def mostrar_frames():
    """Mostrar frames de emoción desde la cola en el hilo principal"""
    try:
        if not frame_queue.empty():
            frame = frame_queue.get()
            cv2.putText(frame, "OA - Análisis emocional", (40, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.imshow("OA - Análisis emocional", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            return
    except:
        pass
    ventana.after(30, mostrar_frames)

def main():
    global ventana, etiqueta
    ventana = tk.Tk()
    ventana.title("OA - Avatar Animado")
    ventana.configure(bg="black")
    ventana.geometry("400x400")

    cargar_frames(ventana)
    etiqueta = tk.Label(ventana, bg="black")
    etiqueta.pack(expand=True)
    ventana.after(100, actualizar_animacion)
    ventana.after(30, mostrar_frames)

    def hilo_logico():
        hablar("Di 'Hola OA' para activar el sistema de tu holograma")
        while True:
            with mic as source:
                print("🎧 Esperando activación...")
                audio = r.listen(source, timeout=None, phrase_time_limit=2)
                try:
                    texto = r.recognize_google(audio, language="es-ES").lower()
                    print(f"🎙️ Escuchado: {texto}")
                except:
                    continue

                if "Hola o a" in texto or "hola escucha" in texto or "oa escucha" in texto or "o a escucha" in texto or "hola oa" in texto or "hola" in texto or "hola hola" in texto:
                    hablar("Te escucho, iniciando escaneo emocional.")
                    emocion = detectar_emocion()
                    mensaje_inicial = respuesta_emocional(emocion)
                    hablar(mensaje_inicial)
                    conversar(emocion)

    threading.Thread(target=hilo_logico, daemon=True).start()
    ventana.mainloop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()