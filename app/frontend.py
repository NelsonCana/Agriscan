import streamlit as st
import requests
from PIL import Image
import io
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="AgriScan - IA Agrícola",
    page_icon="🍅",
    layout="centered"
)

# --- ESTILOS CSS PERSONALIZADOS (Opcional, para dar un toque extra) ---
st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .big-font {
        font-size:20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (BARRA LATERAL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4205/4205565.png", width=100)
    st.title("AgriScan 🍅")
    st.markdown("---")
    st.write("Esta herramienta utiliza **Inteligencia Artificial** (Deep Learning) para diagnosticar enfermedades en hojas de tomate.")
    
    st.info("💡 **Tip:** Asegúrate de que la hoja esté bien iluminada y centrada para un mejor resultado.")
    st.caption("v1.0.0 - Proyecto Integrado")

# --- CABECERA PRINCIPAL ---
st.title("🔬 Diagnóstico de Cultivos")
st.markdown("Sube una fotografía de la hoja afectada para obtener un análisis instantáneo.")
st.markdown("---")

# --- URL DE LA API (Detecta si está en Docker o Local) ---
# Docker pasa la variable API_URL, si no existe usa localhost
API_URL = os.getenv("API_URL", "http://localhost:8000")

# --- LÓGICA DE SUBIDA DE IMAGEN ---
uploaded_file = st.file_uploader("📂 Arrastra tu imagen aquí o haz clic para buscar", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # Mostrar la imagen cargada con un borde redondeado (simulado visualmente)
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagen a analizar", use_container_width=True)

    # Botón de acción
    # Usamos un espacio en blanco para separar un poco
    st.write("") 
    if st.button("🔍 Analizar Estado de la Planta", type="primary", use_container_width=True):
        
        with st.spinner('🤖 La IA está analizando la hoja...'):
            try:
                # Preparamos el archivo para enviarlo a FastAPI
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                # Petición al Backend
                response = requests.post(f"{API_URL}/predict", files=files)

                # --- RESULTADOS ---
                if response.status_code == 200:
                    result = response.json()
                    prediccion = result["prediction"]
                    confianza = result["confidence"]
                    
                    st.markdown("---")
                    st.subheader("📋 Resultados del Análisis")

                    # CONTENEDOR DE MÉTRICAS
                    # Aquí está la MAGIA: [3, 1] da el triple de espacio al nombre para que no se corte
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        # Icono dinámico: Si dice "Sano", ponemos un check verde, si no, una alerta
                        icono = "✅" if "Sano" in prediccion else "🦠"
                        st.metric(label="Diagnóstico", value=f"{icono} {prediccion}")
                    
                    with col2:
                        st.metric(label="Confianza", value=f"{confianza * 100:.1f}%")

                    # Barra de progreso visual
                    st.progress(confianza)

                    # Mensaje final interpretativo
                    if "Sano" in prediccion:
                        st.balloons()
                        st.success("🎉 ¡Buenas noticias! La planta parece estar saludable.")
                    else:
                        st.error(f"⚠️ Atención: Se han detectado signos de **{prediccion}**.")
                        with st.expander("ℹ️ ¿Qué debo hacer?"):
                            st.write("Recomendamos aislar la planta y consultar con un especialista para aplicar el tratamiento adecuado según el diagnóstico.")

                else:
                    st.error(f"Error en el análisis: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("🔌 No se pudo conectar con el servidor (API). Asegúrate de que el backend esté encendido.")
            except Exception as e:
                st.error(f"Ocurrió un error inesperado: {e}")