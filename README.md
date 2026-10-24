# CCNA NetAcad Practice App 🌐

Aplicación interactiva desarrollada en Python y Flet para practicar preguntas y exámenes de preparación para las evaluaciones de **Cisco Networking Academy (NetAcad)**, específicamente orientada a **CCNA 1 v7 (ITN - Introduction to Networks)**.

🚀 **Accede a la aplicación en vivo aquí:**  
👉 **[https://redes-sh74.onrender.com](https://redes-sh74.onrender.com)**

---

## 📋 Características

- **Preguntas oficiales y de práctica:** Basadas en los cuestionarios y exámenes de Cisco NetAcad CCNA 1 (ITNv7).
- **Módulos incluidos:**
  - Módulos 11 - 13: Direccionamiento IP, Subnetting y VLSM
  - Módulos 14 - 15: Capa de Transporte y Aplicación
  - Módulos 16 - 17: Seguridad y Fundamentos de Red
  - Examen Final CCNA 1 (ITNv7)
- **Formatos interactivos:**
  - Opción múltiple (selección única y múltiple).
  - Preguntas de emparejamiento / arrastrar y soltar (*matching*).
  - Soporte de diagramas, topologías y esquemas de red.
- **Interfaz moderna y adaptable:**
  - Compatible con modo claro y oscuro.
  - Guardado de progreso en el navegador.

---

## 🛠️ Tecnologías

- **Lenguaje:** [Python](https://www.python.org/)
- **Framework UI / Web:** [Flet](https://flet.dev/) (`flet`, `flet-web`)
- **Hosting / Despliegue:** [Render](https://render.com/)

---

## 💻 Ejecución en local

Si deseas clonar el proyecto y ejecutarlo en tu entorno local:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Navizuela/appRedes2.git
   cd appRedes2
   ```

2. **Crear y activar un entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux / Mac:
   source .venv/bin/activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación:**
   ```bash
   python examen_gui.py
   ```
   *La aplicación se abrirá automáticamente en tu navegador o ventana de escritorio.*
