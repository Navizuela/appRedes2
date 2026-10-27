# CCNA NetAcad Practice App 🌐

Aplicación web interactiva desarrollada en Python y Flet para practicar preguntas y exámenes de preparación para las certificaciones y evaluaciones de **Cisco Networking Academy (NetAcad)**, abarcando **CCNA 1 v7 (ITN)** y **CCNA 2 v7 (SRWE)**.

**Accede a la aplicación en vivo aquí:**  
**[https://redes-sh74.onrender.com](https://redes-sh74.onrender.com)**

---

## Módulos y Exámenes Disponibles

### 📘 CCNA 1: Introduction to Networks (ITNv7)
- **Módulos 11 - 13:** Direccionamiento IP, Subnetting IPv4/IPv6 y VLSM
- **Módulos 14 - 15:** Capas de Transporte y Aplicación (TCP, UDP, servicios de red)
- **Módulos 16 - 17:** Fundamentos de Seguridad de Red y mitigación de amenazas
- **Examen Final ITNv7:** Evaluación integral del curso completo

### 📙 CCNA 2: Switching, Routing and Wireless Essentials (SRWE v7)
- **Módulos 1 - 4:** Conceptos de conmutación, configuración de switches, VLANs, enlaces troncales (802.1Q, DTP) y enrutamiento entre VLAN (*router-on-a-stick*).
- **Laboratorio de Redes - Prueba 1:** Evaluación práctica de conceptos clave: dominios de colisión/difusión, STP, DTP, asignación de VLANs y enrutamiento inter-VLAN.

---

## Características

- **Formatos de preguntas interactivos:**
  - Opción múltiple (selección simple y selección múltiple).
  - Preguntas de emparejamiento / arrastrar y soltar (*matching* con detección de opciones sin usar).
  - Integración completa de diagramas, topologías, tablas CAM y esquemas de red.
- **Apartados y navegación por cursos:**
  - Filtro por pestañas (`Todos`, `CCNA 1`, `CCNA 2`).
  - Tarjetas visuales organizadas por curso y orden temático.
- **Interfaz moderna y responsiva:**
  - Soporte de modo oscuro y modo claro.
  - Persistencia de progreso y respuestas en el almacenamiento local.
  - Temporizador integrado y revisión detallada de respuestas con explicaciones oficiales.

---

## Tecnologías

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
   *La aplicación se iniciará y estará disponible en `http://localhost:8080` (o el puerto configurado).*
