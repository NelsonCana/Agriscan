from fastapi import FastAPI, File, UploadFile
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os

app = FastAPI()

# --- FUNCIÓN DE AUTO-BÚSQUEDA ---
def encontrar_modelo(filename):
    print(f"🕵️ Buscando '{filename}' en todo el directorio...")
    # Empezamos desde la carpeta actual y subimos/bajamos buscándolo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Buscar en la carpeta actual y subcarpetas
    for root, dirs, files in os.walk(current_dir):
        if filename in files:
            full_path = os.path.join(root, filename)
            print(f"✅ ¡ENCONTRADO! Ruta: {full_path}")
            return full_path
            
    # 2. Si no está, intentamos subir un nivel (por si main.py está en una subcarpeta)
    parent_dir = os.path.dirname(current_dir)
    for root, dirs, files in os.walk(parent_dir):
        if filename in files:
            full_path = os.path.join(root, filename)
            print(f"✅ ¡ENCONTRADO EN PADRE! Ruta: {full_path}")
            return full_path

    return None

# Definimos el nombre exacto del archivo
NOMBRE_ARCHIVO = "agriscan_tomate.h5"

# Ejecutamos la búsqueda
MODEL_PATH = encontrar_modelo(NOMBRE_ARCHIVO)

# Lista de Clases
CLASES = [
    "Tomate - Mancha Bacteriana", "Tomate - Tizón Temprano", "Tomate - Tizón Tardío",
    "Tomate - Moho de la Hoja", "Tomate - Mancha Septoria", "Tomate - Araña Roja",
    "Tomate - Mancha Objetivo", "Tomate - Virus Hoja Amarilla", "Tomate - Virus del Mosaico",
    "Tomate - Sano"
]

model = None

if MODEL_PATH:
    try:
        print(f"🔄 Cargando modelo desde: {MODEL_PATH}")
        model = tf.keras.models.load_model(MODEL_PATH)
        print("🚀 Modelo cargado y listo.")
    except Exception as e:
        print(f"❌ Error al leer el archivo (puede estar corrupto): {e}")
else:
    # --- DIAGNÓSTICO FINAL SI NO LO ENCUENTRA ---
    print("\n🚨🚨 ERROR FATAL: EL ARCHIVO NO ESTÁ EN EL SISTEMA 🚨🚨")
    print(f"Directorio actual de ejecución: {os.getcwd()}")
    print("Archivos visibles aquí:", os.listdir(os.getcwd()))
    print("----------------------------------------------------")
    print("POSIBLES CAUSAS DOCKER:")
    print("1. ¿Tienes un archivo .dockerignore que ignora los .h5?")
    print("2. ¿Tu Dockerfile tiene 'COPY . .' o copia carpetas específicas?")
    print("3. Si el archivo es muy grande, quizás git no lo subió.")

def preprocess_image(image_data):
    image = Image.open(io.BytesIO(image_data))
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize((224, 224))
    img_array = np.array(image)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

@app.get("/")
def home():
    return {
        "status": "online",
        "model_found": MODEL_PATH is not None,
        "path_used": MODEL_PATH if MODEL_PATH else "NO ENCONTRADO"
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        return {"error": "El modelo no se encontró en el servidor. Revisa los logs."}
    
    try:
        contents = await file.read()
        processed_image = preprocess_image(contents)
        prediction = model.predict(processed_image)
        index = np.argmax(prediction)
        confidence = float(np.max(prediction))
        result = CLASES[index]
        return {"filename": file.filename, "prediction": result, "confidence": confidence}
    except Exception as e:
        return {"error": str(e)}