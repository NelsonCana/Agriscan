# 🍅 AgriScan: Diagnóstico de Cultivos con IA

> **Proyecto Integrado de Machine Learning e Inteligencia Artificial**
> *Integrantes:* Nelson Caña, Felipe Castro

## 📖 Descripción
AgriScan es una solución de **Deep Learning** diseñada para detectar enfermedades en hojas de tomate en tiempo real. Utiliza una arquitectura de **Microservicios** (API + Frontend) contenerizada en **Docker**, permitiendo un despliegue ágil en cualquier servidor.

El modelo actual clasifica 10 patologías con una precisión del **94.5%**, utilizando **Transfer Learning** sobre la arquitectura **MobileNetV2**.

---

## 🏗️ Arquitectura Técnica
La solución consta de tres módulos principales:

1.  **Cerebro (Model):** Red Neuronal Convolucional (MobileNetV2) entrenada con el dataset *PlantVillage*.
2.  **Backend (API):** Desarrollado en **FastAPI**, expone el endpoint `/predict` y gestiona la inferencia.
3.  **Frontend (UI):** Interfaz desarrollada en **Streamlit** para la interacción con el agricultor.

```mermaid
graph LR
  A[Usuario] -- Sube Imagen --> B(Frontend / Streamlit)
  B -- POST Request --> C(Backend / FastAPI)
  C -- Carga .h5 --> D[Modelo MobileNetV2]
  D -- Predicción --> C
  C -- JSON --> B
  B -- Resultado Visual --> A
