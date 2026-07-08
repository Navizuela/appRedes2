import flet as ft
import json
import os

def main(page: ft.Page):
    page.title = "Examen CCNA - Cisco"
    page.theme_mode = ft.ThemeMode.LIGHT

    state = {"preguntas": [], "indice": 0, "puntaje": 0}
    container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
    page.add(container)

    def cargar_examen(ruta):
        with open(ruta, 'r', encoding='utf-8') as f:
            state["preguntas"] = json.load(f)
        state["indice"] = 0
        state["puntaje"] = 0
        mostrar_pregunta()

    def mostrar_pregunta():
        container.controls.clear()
        q = state["preguntas"][state["indice"]]
        container.controls.append(ft.Text(f"Pregunta {state['indice'] + 1}", weight="bold", size=18))
        container.controls.append(ft.Text(q["pregunta"], size=16))

        if "imagen" in q and q["imagen"]:
            ruta_img = os.path.join("img", q["imagen"])
            if os.path.exists(ruta_img):
                container.controls.append(ft.Image(src=ruta_img, width=400))

        feedback_container = ft.Column()
        tipo = q.get("tipo", "opcion_multiple")

        if tipo == "emparejamiento":
            dropdowns = []
            for obj in q["objetivos"]:
                dd = ft.Dropdown(label=obj, options=[ft.dropdown.Option(o) for o in q["opciones"]])
                dropdowns.append(dd)
                container.controls.append(dd)

            def verificar_emp(e):
                respuestas = {obj: dd.value for obj, dd in zip(q["objetivos"], dropdowns)}
                if any(v is None for v in respuestas.values()): return
                aciertos = all(respuestas[obj] == q["respuestas_correctas"].get(obj) for obj in q["objetivos"])
                finalizar(aciertos, q, feedback_container)
            container.controls.append(ft.Button(content=ft.Text("Confirmar"), on_click=verificar_emp))

        else:
            # --- Lógica inteligente: ¿Múltiple o Única? ---
            resp_correctas = q.get("respuestas_correctas")
            es_multiple = isinstance(resp_correctas, list) and len(resp_correctas) > 1

            if es_multiple:
                cbs = [ft.Checkbox(label=op) for op in q["opciones"]]
                for cb in cbs: container.controls.append(cb)
                def verif_multi(e):
                    seleccionados = [i for i, cb in enumerate(cbs) if cb.value]
                    # Compara listas ordenadas
                    es_correcto = sorted(seleccionados) == sorted(resp_correctas)
                    finalizar(es_correcto, q, feedback_container)
                container.controls.append(ft.Button(content=ft.Text("Confirmar"), on_click=verif_multi))
            else:
                rg = ft.RadioGroup(content=ft.Column([ft.Radio(value=str(i), label=op) for i, op in enumerate(q["opciones"])]))
                container.controls.append(rg)
                def verif_radio(e):
                    val_c = resp_correctas[0] if isinstance(resp_correctas, list) else resp_correctas
                    es_correcto = rg.value is not None and int(rg.value) == val_c
                    finalizar(es_correcto, q, feedback_container)
                container.controls.append(ft.Button(content=ft.Text("Confirmar"), on_click=verif_radio))

        container.controls.append(feedback_container)
        page.update()

    # ... (Funciones finalizar y siguiente se mantienen igual)
    def finalizar(es_correcto, q, fb_container):
        if es_correcto: state["puntaje"] += 1
        fb_container.controls.clear()
        fb_container.controls.append(ft.Text("✔️ ¡Correcto!" if es_correcto else "❌ Incorrecto", color="green" if es_correcto else "red", weight="bold"))
        if "explicacion" in q: fb_container.controls.append(ft.Text(f"💡 {q['explicacion']}", italic=True))
        fb_container.controls.append(ft.Button(content=ft.Text("Siguiente"), on_click=lambda e: siguiente()))
        page.update()

    def siguiente():
        state["indice"] += 1
        if state["indice"] < len(state["preguntas"]): mostrar_pregunta()
        else:
            container.controls.clear()
            container.controls.append(ft.Text(f"Examen Finalizado", size=24, weight="bold"))
            container.controls.append(ft.Text(f"Puntaje: {state['puntaje']} / {len(state['preguntas'])}"))
            container.controls.append(ft.Button(content=ft.Text("Volver al Menú"), on_click=lambda e: mostrar_menu()))
            page.update()

    mostrar_menu()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    ft.app(target=main, port=port, view=ft.AppView.WEB_BROWSER)
