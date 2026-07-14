import asyncio
import inspect
import json
import os

import flet as ft


STORAGE_KEY = "ccna_exam_progress_v1"
THEME_STORAGE_KEY = "ccna_exam_theme_v1"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "img")
VALOR_SIN_ASIGNAR = "__sin_asignar__"


async def main(page: ft.Page):
    page.title = "Examen CCNA - Cisco"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.HIDDEN

    state = {
        "preguntas": [],
        "ruta": None,
        "indice": 0,
        "puntaje": 0,
        "resultados": [],
        "respuestas_usuario": [],
        "respondida": False,
        "ultima_correcta": None,
        "finalizado": False,
        "tema": "dark",
        "tiempo_segundos": 0,
    }
    container = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )
    content = ft.Container(
        content=container,
        expand=True,
        padding=ft.Padding(left=16, top=16, right=16, bottom=88),
    )
    imagen_precarga = ft.Image(src="", width=1, height=1, opacity=0)
    timer_ref = {"control": None}
    guardado_ref = {"task": None, "dirty": False}
    page.add(content)
    page.overlay.append(imagen_precarga)

    def es_movil():
        return bool(page.width and page.width < 600)

    def ancho_disponible(maximo=None):
        ancho = max((page.width or 400) - 32, 240)
        return min(ancho, maximo) if maximo else ancho

    def ancho_boton():
        return ancho_disponible() if es_movil() else None

    async def mostrar_indicador_boton(e, texto="Registrando..."):
        """Confirma visualmente el clic mientras se procesa la acción."""
        boton = getattr(e, "control", None)
        if boton is not None:
            boton.disabled = True
            boton.content = ft.Row(
                [
                    ft.ProgressRing(width=18, height=18, stroke_width=2),
                    ft.Text(texto),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                tight=True,
            )
            page.update()
            # Cede el control para enviar el cambio visual antes de continuar.
            await asyncio.sleep(0)

    def obtener_ruta_imagen(nombre_imagen):
        """Devuelve la URL pública y la ruta local de una imagen del examen."""
        if not nombre_imagen or not state.get("ruta"):
            return None, None

        nombre_examen = os.path.splitext(os.path.basename(state["ruta"]))[0]
        nombre_seguro = os.path.basename(nombre_imagen)
        ruta_relativa = os.path.join(nombre_examen, nombre_seguro)
        ruta_local = os.path.join(IMAGES_DIR, ruta_relativa)
        ruta_publica = "/" + ruta_relativa.replace(os.sep, "/")
        return ruta_publica, ruta_local

    def precargar_siguiente_imagen():
        """Descarga en segundo plano la próxima imagen para aprovechar la caché."""
        imagen_precarga.src = ""
        for pregunta in state["preguntas"][state["indice"] + 1:]:
            if not pregunta.get("imagen"):
                continue
            src, ruta_local = obtener_ruta_imagen(pregunta["imagen"])
            if ruta_local and os.path.isfile(ruta_local):
                imagen_precarga.src = src
            break

    async def resolver_si_es_async(resultado):
        if not inspect.isawaitable(resultado):
            return resultado
        return await resultado

    def obtener_storage():
        return getattr(page, "shared_preferences", None) or getattr(page, "client_storage", None)

    async def obtener_estado_guardado():
        storage = obtener_storage()
        if storage is None:
            return None
        try:
            data = await resolver_si_es_async(storage.get(STORAGE_KEY))
        except Exception:
            return None
        if not data:
            return None
        if isinstance(data, dict):
            return data
        try:
            return json.loads(data)
        except (TypeError, json.JSONDecodeError):
            return None

    async def guardar_estado():
        storage = obtener_storage()
        if storage is None or not state["ruta"]:
            return
        data = {
            "ruta": state["ruta"],
            "indice": state["indice"],
            "puntaje": state["puntaje"],
            "resultados": state["resultados"],
            "respuestas_usuario": state["respuestas_usuario"],
            "respondida": state["respondida"],
            "ultima_correcta": state["ultima_correcta"],
            "finalizado": state["finalizado"],
            "tiempo_segundos": state["tiempo_segundos"],
        }
        try:
            await resolver_si_es_async(storage.set(STORAGE_KEY, json.dumps(data)))
        except Exception:
            pass

    async def ejecutar_guardado_diferido():
        """Agrupa cambios cercanos en una sola escritura al navegador."""
        try:
            while guardado_ref["dirty"]:
                await asyncio.sleep(0.35)
                guardado_ref["dirty"] = False
                await guardar_estado()
        finally:
            guardado_ref["task"] = None
            if guardado_ref["dirty"]:
                programar_guardado()

    def programar_guardado():
        guardado_ref["dirty"] = True
        tarea = guardado_ref["task"]
        if tarea is None or tarea.done():
            guardado_ref["task"] = asyncio.create_task(ejecutar_guardado_diferido())

    def cancelar_guardado_pendiente():
        guardado_ref["dirty"] = False
        tarea = guardado_ref.get("task")
        if tarea is not None and not tarea.done():
            tarea.cancel()
        guardado_ref["task"] = None

    async def borrar_estado_guardado():
        cancelar_guardado_pendiente()
        storage = obtener_storage()
        if storage is None:
            return
        try:
            await resolver_si_es_async(storage.remove(STORAGE_KEY))
        except Exception:
            pass

    async def obtener_tema_guardado():
        storage = obtener_storage()
        if storage is None:
            return None
        try:
            return await resolver_si_es_async(storage.get(THEME_STORAGE_KEY))
        except Exception:
            return None

    async def guardar_tema():
        storage = obtener_storage()
        if storage is None:
            return
        try:
            await resolver_si_es_async(storage.set(THEME_STORAGE_KEY, state["tema"]))
        except Exception:
            pass

    def entero_seguro(valor, default=0):
        try:
            return int(valor)
        except (TypeError, ValueError):
            return default

    def reiniciar_state():
        state["preguntas"] = []
        state["ruta"] = None
        state["indice"] = 0
        state["puntaje"] = 0
        state["resultados"] = []
        state["respuestas_usuario"] = []
        state["respondida"] = False
        state["ultima_correcta"] = None
        state["finalizado"] = False
        state["tiempo_segundos"] = 0

    def preparar_resultados(total):
        resultados = state.get("resultados") or []
        respuestas_usuario = state.get("respuestas_usuario") or []
        state["resultados"] = (resultados + [None] * total)[:total]
        state["respuestas_usuario"] = (respuestas_usuario + [None] * total)[:total]

    def pregunta_respondida(indice=None):
        indice = state["indice"] if indice is None else indice
        return state["resultados"][indice] is not None

    def permite_opciones_sin_usar(q):
        texto = (q.get("pregunta") or "").lower()
        return "no se utilizan todas las opciones" in texto

    def resultado_actual():
        return state["resultados"][state["indice"]]

    def sincronizar_estado_pregunta():
        resultado = resultado_actual() if state["resultados"] else None
        state["respondida"] = resultado is not None
        state["ultima_correcta"] = resultado

    def recalcular_puntaje():
        state["puntaje"] = sum(1 for resultado in state["resultados"] if resultado is True)

    def formatear_tiempo():
        segundos = max(entero_seguro(state.get("tiempo_segundos")), 0)
        minutos = segundos // 60
        resto = segundos % 60
        return f"{minutos:02d}:{resto:02d}"

    def color_tiempo():
        if state.get("tiempo_segundos", 0) >= 3600:
            return "#ef4444"
        return "#e5e7eb" if state["tema"] == "dark" else "#111827"

    def actualizar_texto_tiempo():
        control = timer_ref.get("control")
        if control is None:
            return
        control.value = f"Tiempo {formatear_tiempo()}"
        control.color = color_tiempo()

    async def contador_tiempo():
        while True:
            await asyncio.sleep(1)
            if not state["preguntas"] or state["finalizado"]:
                continue
            state["tiempo_segundos"] += 1
            actualizar_texto_tiempo()
            if state["tiempo_segundos"] % 10 == 0:
                programar_guardado()
            try:
                control = timer_ref.get("control")
                if control is not None:
                    control.update()
            except Exception:
                pass

    def aplicar_tema():
        page.theme_mode = ft.ThemeMode.DARK if state["tema"] == "dark" else ft.ThemeMode.LIGHT
        actualizar_texto_tiempo()

    def texto_boton_tema():
        return "Modo claro" if state["tema"] == "dark" else "Modo oscuro"

    async def cambiar_tema():
        state["tema"] = "light" if state["tema"] == "dark" else "dark"
        aplicar_tema()
        await guardar_tema()
        await refrescar_vista_actual()

    async def click_cambiar_tema(e):
        await cambiar_tema()

    def crear_boton_tema(ancho_adaptable=True, expandir=False):
        return ft.Button(
            content=ft.Text(
                texto_boton_tema(),
                size=11 if es_movil() and expandir else None,
                text_align=ft.TextAlign.CENTER,
            ),
            on_click=click_cambiar_tema,
            width=ancho_boton() if ancho_adaptable else None,
            expand=expandir,
        )

    def crear_barra_acciones_examen():
        return ft.Row(
            [
                crear_boton_tema(ancho_adaptable=False, expandir=True),
                ft.Button(
                    content=ft.Text("Volver al menú", size=11 if es_movil() else None, text_align=ft.TextAlign.CENTER),
                    on_click=click_volver_al_menu,
                    expand=True,
                ),
                ft.Button(
                    content=ft.Text("Reintentar", size=11 if es_movil() else None, text_align=ft.TextAlign.CENTER),
                    on_click=click_reintentar,
                    expand=True,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        )

    async def refrescar_vista_actual():
        if state["preguntas"]:
            if state["finalizado"]:
                mostrar_resultado()
            else:
                mostrar_pregunta()
        else:
            await mostrar_menu()

    async def volver_al_menu():
        await borrar_estado_guardado()
        reiniciar_state()
        actualizar_boton_reintentar()
        await mostrar_menu()

    def cerrar_confirmacion(e=None):
        page.pop_dialog()

    async def confirmar_volver_al_menu(e):
        page.pop_dialog()
        await volver_al_menu()

    async def click_volver_al_menu(e):
        if not state["preguntas"]:
            await volver_al_menu()
            return

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Text("¿Volver al menú?"),
            content=ft.Text(
                "El progreso de este examen no será guardado y se eliminarán "
                "las respuestas registradas."
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=cerrar_confirmacion),
                ft.Button(content=ft.Text("Volver al menú"), on_click=confirmar_volver_al_menu),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dialogo)

    def actualizar_boton_reintentar():
        page.floating_action_button = None

    def mostrar_resultado():
        container.controls.clear()
        actualizar_boton_reintentar()
        container.controls.append(crear_barra_acciones_examen())
        container.controls.append(crear_barra_examen())
        container.controls.append(ft.Text("Examen Finalizado", size=24, weight="bold"))
        container.controls.append(ft.Text(f"Puntaje: {state['puntaje']} / {len(state['preguntas'])}"))
        page.update()

    def mostrar_feedback(q, fb_container):
        es_correcto = bool(resultado_actual())
        fb_container.controls.clear()
        fb_container.controls.append(
            ft.Text(
                "Correcto" if es_correcto else "Incorrecto",
                color="green" if es_correcto else "red",
                weight="bold",
            )
        )
        if q.get("explicacion"):
            fb_container.controls.append(ft.Text(q["explicacion"], italic=True))
        if state["indice"] < len(state["preguntas"]) - 1:
            fb_container.controls.append(ft.Button(content=ft.Text("Siguiente"), on_click=click_siguiente))
        else:
            fb_container.controls.append(ft.Button(content=ft.Text("Finalizar"), on_click=click_siguiente))

    def resumen_respuesta(q):
        respuesta = state["respuestas_usuario"][state["indice"]]
        if respuesta is None:
            return None
        if isinstance(respuesta, dict):
            partes = [f"{clave}: {valor}" for clave, valor in respuesta.items()]
            return "Tu respuesta: " + "; ".join(partes)
        if isinstance(respuesta, list):
            opciones = q.get("opciones", [])
            elegidas = [opciones[i] for i in respuesta if isinstance(i, int) and 0 <= i < len(opciones)]
            return "Tu respuesta: " + ", ".join(elegidas)
        return f"Tu respuesta: {respuesta}"

    def colores_revision():
        es_oscuro = state["tema"] == "dark"
        return {
            "neutral_bg": "#111827" if es_oscuro else "#f8fafc",
            "neutral_border": "#374151" if es_oscuro else "#d5dce6",
            "neutral_text": "#e5e7eb" if es_oscuro else "#111827",
            "muted_text": "#9ca3af" if es_oscuro else "#4b5563",
            "correct_bg": "#064e3b" if es_oscuro else "#d9f2e4",
            "correct_border": "#10b981" if es_oscuro else "#7bc99a",
            "correct_text": "#bbf7d0" if es_oscuro else "#136c3a",
            "wrong_bg": "#7f1d1d" if es_oscuro else "#fde2e2",
            "wrong_border": "#ef4444" if es_oscuro else "#e38b8b",
            "wrong_text": "#fecaca" if es_oscuro else "#9f1f1f",
        }

    def crear_tarjeta_revision(texto_principal, etiqueta=None, estado="neutral"):
        colores = colores_revision()
        if estado == "correct":
            bgcolor = colores["correct_bg"]
            border_color = colores["correct_border"]
            text_color = colores["correct_text"]
        elif estado == "wrong":
            bgcolor = colores["wrong_bg"]
            border_color = colores["wrong_border"]
            text_color = colores["wrong_text"]
        else:
            bgcolor = colores["neutral_bg"]
            border_color = colores["neutral_border"]
            text_color = colores["neutral_text"]

        textos = [ft.Text(texto_principal, color=text_color)]
        if etiqueta:
            textos.append(ft.Text(etiqueta, color=text_color, weight="bold", size=12))

        return ft.Container(
            bgcolor=bgcolor,
            border=ft.Border(
                left=ft.BorderSide(1, border_color),
                top=ft.BorderSide(1, border_color),
                right=ft.BorderSide(1, border_color),
                bottom=ft.BorderSide(1, border_color),
            ),
            border_radius=4,
            padding=ft.Padding(left=10, top=8, right=10, bottom=8),
            width=ancho_disponible(),
            content=ft.Column(textos, spacing=3),
        )

    def mostrar_alternativas_revisadas(q):
        tipo = q.get("tipo", "opcion_multiple")
        respuesta = state["respuestas_usuario"][state["indice"]]

        if tipo == "emparejamiento":
            if q.get("opciones"):
                container.controls.append(ft.Text("Alternativas disponibles: " + ", ".join(q["opciones"])))

            respuestas_usuario = respuesta if isinstance(respuesta, dict) else {}
            correctas = q.get("respuestas_correctas", {})
            for obj in q.get("objetivos", []):
                seleccion = respuestas_usuario.get(obj)
                correcta = correctas.get(obj)
                estado = "correct" if seleccion == correcta else "wrong"
                textos = [
                    f"{obj}",
                    f"Tu respuesta: {seleccion if seleccion else 'Sin respuesta'}",
                    f"Correcta: {correcta}",
                ]
                container.controls.append(crear_tarjeta_revision("\n".join(textos), estado=estado))
            return

        opciones = q.get("opciones", [])
        correctas = q.get("respuestas_correctas", [])
        if not isinstance(correctas, list):
            correctas = [correctas]
        seleccionadas = respuesta if isinstance(respuesta, list) else []
        letras = ["A", "B", "C", "D", "E", "F", "G", "H"]

        for i, opcion in enumerate(opciones):
            es_correcta = i in correctas
            fue_seleccionada = i in seleccionadas
            if es_correcta and fue_seleccionada:
                estado = "correct"
                etiqueta = "Correcta - tu respuesta"
            elif es_correcta:
                estado = "correct"
                etiqueta = "Correcta"
            elif fue_seleccionada:
                estado = "wrong"
                etiqueta = "Tu respuesta - incorrecta"
            else:
                estado = "neutral"
                etiqueta = None

            letra = letras[i] if i < len(letras) else str(i + 1)
            container.controls.append(crear_tarjeta_revision(f"{letra}. {opcion}", etiqueta, estado))

    async def finalizar(es_correcto, q, fb_container, respuesta_usuario=None):
        if pregunta_respondida():
            mostrar_feedback(q, fb_container)
            page.update()
            return

        state["resultados"][state["indice"]] = bool(es_correcto)
        state["respuestas_usuario"][state["indice"]] = respuesta_usuario
        sincronizar_estado_pregunta()
        recalcular_puntaje()
        programar_guardado()
        mostrar_pregunta()

    async def navegar_a(indice):
        if indice < 0 or indice >= len(state["preguntas"]):
            return
        if not state["finalizado"] and indice > state["indice"] and not pregunta_respondida(state["indice"]):
            return
        state["indice"] = indice
        sincronizar_estado_pregunta()
        programar_guardado()
        mostrar_pregunta()

    def crear_click_navegar(indice):
        async def click_navegar(e):
            await navegar_a(indice)

        return click_navegar

    def crear_barra_examen():
        total = len(state["preguntas"])
        es_oscuro = state["tema"] == "dark"
        barra_bg = "#111827" if es_oscuro else "#f5f7fa"
        barra_borde = "#374151" if es_oscuro else "#d5dce6"
        titulo_color = "#60a5fa" if es_oscuro else "#0b5cab"
        texto_info_color = "#e5e7eb" if es_oscuro else "#111827"
        activo_bg = "#2563eb" if es_oscuro else "#0b5cab"
        activo_borde = "#60a5fa" if es_oscuro else "#0b5cab"
        correcta_bg = "#064e3b" if es_oscuro else "#d9f2e4"
        correcta_color = "#bbf7d0" if es_oscuro else "#136c3a"
        incorrecta_bg = "#7f1d1d" if es_oscuro else "#fde2e2"
        incorrecta_color = "#fecaca" if es_oscuro else "#9f1f1f"
        pendiente_bg = "#1f2937" if es_oscuro else "#eef2f7"
        pendiente_color = "#9ca3af" if es_oscuro else "#4b5563"
        item_borde = "#4b5563" if es_oscuro else "#b8c4d4"
        timer_ref["control"] = ft.Text(f"Tiempo {formatear_tiempo()}", color=color_tiempo())
        controles = []
        if total <= 20:
            indices_visibles = list(range(total))
        else:
            inicio = max(0, state["indice"] - 5)
            fin = min(total, state["indice"] + 6)
            indices_visibles = sorted({0, total - 1, *range(inicio, fin)})

        indice_anterior = None
        for i in indices_visibles:
            if indice_anterior is not None and i - indice_anterior > 1:
                controles.append(ft.Text("…", color=pendiente_color, width=20, text_align=ft.TextAlign.CENTER))
            resultado = state["resultados"][i] if i < len(state["resultados"]) else None
            if i == state["indice"]:
                bgcolor = activo_bg
                color = "white"
            elif resultado is True:
                bgcolor = correcta_bg
                color = correcta_color
            elif resultado is False:
                bgcolor = incorrecta_bg
                color = incorrecta_color
            else:
                bgcolor = pendiente_bg
                color = pendiente_color

            puede_navegar = state["finalizado"] or i <= state["indice"] or resultado is not None
            border_color = item_borde if i != state["indice"] else activo_borde
            controles.append(
                ft.Container(
                    content=ft.Row(
                        [ft.Text(str(i + 1), color=color, weight="bold")],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    width=36,
                    height=30,
                    bgcolor=bgcolor,
                    border_radius=4,
                    border=ft.Border(
                        left=ft.BorderSide(1, border_color),
                        top=ft.BorderSide(1, border_color),
                        right=ft.BorderSide(1, border_color),
                        bottom=ft.BorderSide(1, border_color),
                    ),
                    on_click=crear_click_navegar(i) if puede_navegar else None,
                    opacity=1 if puede_navegar else 0.45,
                )
            )
            indice_anterior = i

        return ft.Container(
            bgcolor=barra_bg,
            border=ft.Border(bottom=ft.BorderSide(1, barra_borde)),
            padding=ft.Padding(left=10, top=8, right=10, bottom=8),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Cisco Academy", weight="bold", color=titulo_color),
                            ft.Text(f"Pregunta {state['indice'] + 1} de {total}", color=texto_info_color),
                            timer_ref["control"],
                            ft.Text(f"Puntaje {state['puntaje']} / {total}", color=texto_info_color),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        wrap=True,
                        spacing=12,
                        run_spacing=6,
                    ),
                    ft.Row(controles, scroll=ft.ScrollMode.AUTO, spacing=4),
                ],
                spacing=8,
            ),
        )

    async def reintentar_examen():
        state["indice"] = 0
        state["puntaje"] = 0
        state["resultados"] = [None] * len(state["preguntas"])
        state["respuestas_usuario"] = [None] * len(state["preguntas"])
        state["respondida"] = False
        state["ultima_correcta"] = None
        state["finalizado"] = False
        state["tiempo_segundos"] = 0
        programar_guardado()
        mostrar_pregunta()

    async def click_reintentar(e):
        await reintentar_examen()

    async def finalizar_desde_ultima():
        state["finalizado"] = True
        programar_guardado()
        mostrar_resultado()

    async def siguiente():
        if state["indice"] >= len(state["preguntas"]) - 1:
            await finalizar_desde_ultima()
            return

        state["indice"] += 1
        sincronizar_estado_pregunta()
        programar_guardado()
        mostrar_pregunta()

    async def click_siguiente(e):
        await mostrar_indicador_boton(
            e,
            "Finalizando..." if state["indice"] >= len(state["preguntas"]) - 1 else "Cargando...",
        )
        await siguiente()

    def mostrar_pregunta():
        container.controls.clear()
        actualizar_boton_reintentar()
        if not state["preguntas"]:
            container.controls.append(ft.Text("No hay preguntas cargadas.", color="red"))
            page.update()
            return

        q = state["preguntas"][state["indice"]]
        sincronizar_estado_pregunta()
        precargar_siguiente_imagen()
        container.controls.append(crear_barra_acciones_examen())
        container.controls.append(crear_barra_examen())
        container.controls.append(ft.Text(f"Pregunta {state['indice'] + 1} de {len(state['preguntas'])}", weight="bold", size=18))
        if state["finalizado"]:
            container.controls.append(ft.Button(content=ft.Text("Ver resultado"), on_click=lambda e: mostrar_resultado()))
        container.controls.append(ft.Text(q["pregunta"], size=16))

        if q.get("imagen"):
            src_img, ruta_img = obtener_ruta_imagen(q["imagen"])
            if ruta_img and os.path.isfile(ruta_img):
                container.controls.append(
                    ft.Container(
                        content=ft.Image(
                            src=src_img,
                            width=ancho_disponible(640),
                            fit=ft.BoxFit.CONTAIN,
                            border_radius=8,
                        ),
                        alignment=ft.Alignment.CENTER,
                        width=ancho_disponible(),
                    )
                )
            else:
                container.controls.append(
                    ft.Text(
                        f"Imagen no disponible: {q['imagen']}",
                        color="#f59e0b",
                        italic=True,
                    )
                )

        feedback_container = ft.Column()
        tipo = q.get("tipo", "opcion_multiple")
        resp_correctas = q.get("respuestas_correctas")

        if state["respondida"]:
            mostrar_alternativas_revisadas(q)
            mostrar_feedback(q, feedback_container)
        elif tipo == "emparejamiento":
            dropdowns = []
            permite_vacias = permite_opciones_sin_usar(q)
            for obj in q["objetivos"]:
                opciones_dropdown = []
                if permite_vacias:
                    opciones_dropdown.append(
                        ft.dropdown.Option(
                            key=VALOR_SIN_ASIGNAR,
                            text="— Sin asignar —",
                        )
                    )
                opciones_dropdown.extend(ft.dropdown.Option(o) for o in q["opciones"])
                dd = ft.Dropdown(
                    label=obj,
                    options=opciones_dropdown,
                    width=ancho_disponible(),
                )
                dropdowns.append(dd)
                container.controls.append(dd)

            async def verificar_emp(e):
                respuestas = {
                    obj: None if dd.value == VALOR_SIN_ASIGNAR else dd.value
                    for obj, dd in zip(q["objetivos"], dropdowns)
                }
                cantidad_respondida = sum(valor is not None for valor in respuestas.values())
                if permite_vacias:
                    if cantidad_respondida != len(q["respuestas_correctas"]):
                        return
                elif cantidad_respondida != len(q["objetivos"]):
                    return
                await mostrar_indicador_boton(e)
                aciertos = all(respuestas[obj] == q["respuestas_correctas"].get(obj) for obj in q["objetivos"])
                await finalizar(aciertos, q, feedback_container, respuestas)

            container.controls.append(ft.Button(content=ft.Text("Confirmar"), on_click=verificar_emp))
        else:
            es_multiple = isinstance(resp_correctas, list) and len(resp_correctas) > 1
            if es_multiple:
                cbs = [ft.Checkbox(label=op) for op in q["opciones"]]
                for cb in cbs:
                    container.controls.append(cb)

                async def verif_multi(e):
                    seleccionados = [i for i, cb in enumerate(cbs) if cb.value]
                    await mostrar_indicador_boton(e)
                    await finalizar(sorted(seleccionados) == sorted(resp_correctas), q, feedback_container, seleccionados)

                container.controls.append(ft.Button(content=ft.Text("Confirmar"), on_click=verif_multi))
            else:
                rg = ft.RadioGroup(content=ft.Column([ft.Radio(value=str(i), label=op) for i, op in enumerate(q["opciones"])]))
                container.controls.append(rg)

                async def verif_radio(e):
                    val_c = resp_correctas[0] if isinstance(resp_correctas, list) else resp_correctas
                    seleccion = [int(rg.value)] if rg.value is not None else []
                    if rg.value is None:
                        return
                    await mostrar_indicador_boton(e)
                    await finalizar(rg.value is not None and int(rg.value) == val_c, q, feedback_container, seleccion)

                container.controls.append(ft.Button(content=ft.Text("Confirmar"), on_click=verif_radio))

        container.controls.append(feedback_container)
        page.update()

    async def cargar_examen(ruta, progreso=None):
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                preguntas = json.load(f)

            if not preguntas:
                raise ValueError("El archivo no tiene preguntas.")

            state["preguntas"] = preguntas
            state["ruta"] = ruta
            state["indice"] = 0
            state["puntaje"] = 0
            state["resultados"] = []
            state["respuestas_usuario"] = []
            state["respondida"] = False
            state["ultima_correcta"] = None
            state["finalizado"] = False
            state["tiempo_segundos"] = 0

            if progreso:
                ultimo_indice = max(len(state["preguntas"]) - 1, 0)
                state["indice"] = min(max(entero_seguro(progreso.get("indice")), 0), ultimo_indice)
                state["puntaje"] = max(entero_seguro(progreso.get("puntaje")), 0)
                if isinstance(progreso.get("resultados"), list):
                    state["resultados"] = progreso["resultados"]
                if isinstance(progreso.get("respuestas_usuario"), list):
                    state["respuestas_usuario"] = progreso["respuestas_usuario"]
                state["respondida"] = bool(progreso.get("respondida", False))
                state["ultima_correcta"] = progreso.get("ultima_correcta")
                state["finalizado"] = bool(progreso.get("finalizado", False))
                state["tiempo_segundos"] = max(entero_seguro(progreso.get("tiempo_segundos")), 0)

            preparar_resultados(len(state["preguntas"]))
            if progreso and "resultados" not in progreso and state["respondida"]:
                state["resultados"][state["indice"]] = bool(state["ultima_correcta"])
            sincronizar_estado_pregunta()
            recalcular_puntaje()
            await guardar_estado()
            if state["finalizado"]:
                mostrar_resultado()
            else:
                mostrar_pregunta()
        except Exception as e:
            container.controls.append(ft.Text(f"Error al cargar archivo: {e}", color="red"))
            page.update()

    async def restaurar_estado_guardado():
        progreso = await obtener_estado_guardado()
        if not progreso:
            return False

        ruta = progreso.get("ruta")
        if not ruta or not os.path.exists(ruta):
            await borrar_estado_guardado()
            return False

        await cargar_examen(ruta, progreso)
        return True

    async def click_continuar(e):
        await restaurar_estado_guardado()

    async def click_borrar_progreso(e):
        await volver_al_menu()

    def crear_click_cargar(ruta):
        async def click_cargar(e):
            await cargar_examen(ruta)

        return click_cargar

    async def mostrar_menu():
        container.controls.clear()
        actualizar_boton_reintentar()
        container.controls.append(crear_boton_tema())
        container.controls.append(ft.Text("Selecciona el modulo:", size=24, weight="bold"))

        progreso = await obtener_estado_guardado()
        if progreso and progreso.get("ruta") and os.path.exists(progreso["ruta"]):
            container.controls.append(ft.Button(content=ft.Text("Continuar examen guardado"), on_click=click_continuar, width=ancho_boton()))
            container.controls.append(ft.Button(content=ft.Text("Borrar progreso guardado"), on_click=click_borrar_progreso, width=ancho_boton()))

        if os.path.exists("json"):
            for archivo in [f for f in os.listdir("json") if f.endswith(".json")]:
                ruta = os.path.join("json", archivo)
                btn = ft.Button(
                    content=ft.Text(f"Iniciar {archivo.replace('.json', '').upper()}"),
                    on_click=crear_click_cargar(ruta),
                    width=ancho_boton(),
                )
                container.controls.append(btn)
        else:
            container.controls.append(ft.Text("Carpeta 'json' no encontrada.", color="red"))
        page.update()

    tema_guardado = await obtener_tema_guardado()
    if tema_guardado in ("dark", "light"):
        state["tema"] = tema_guardado
    aplicar_tema()
    asyncio.create_task(contador_tiempo())

    if not await restaurar_estado_guardado():
        await mostrar_menu()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, port=port, view=ft.AppView.WEB_BROWSER, assets_dir=IMAGES_DIR)
