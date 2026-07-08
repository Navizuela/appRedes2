import json
import random

def cargar_preguntas(ruta_archivo):
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_archivo}'.")
        return []
    except json.JSONDecodeError:
        print("Error: El archivo JSON tiene un formato inválido.")
        return []

def realizar_prueba():
    preguntas = cargar_preguntas('preguntas.json')
    if not preguntas:
        return

    random.shuffle(preguntas)
    puntaje = 0
    total_preguntas = len(preguntas)

    print("="*60)
    print(" EXAMEN DE OPTIMIZACIÓN Y MONITOREO DE REDES (CCNA)")
    print("="*60)

    for i, q in enumerate(preguntas):
        print(f"\nPregunta {i + 1} de {total_preguntas}:")
        print(q["pregunta"])
        
        letras = ['A', 'B', 'C', 'D', 'E', 'F']
        opciones = q["opciones"]
        opciones_con_letras = list(zip(letras[:len(opciones)], opciones))
        
        for letra, opcion in opciones_con_letras:
            print(f"  {letra}) {opcion}")
            
        respuestas_correctas = q["respuestas_correctas"]
        es_multiple = len(respuestas_correctas) > 1

        # Instrucciones de entrada
        if es_multiple:
            print(f"\n(Selecciona {len(respuestas_correctas)} opciones. Ejemplo: A, C)")
        else:
            print("\n(Selecciona 1 opción. Ejemplo: B)")

        # Capturar y procesar respuesta del usuario
        entrada_valida = False
        while not entrada_valida:
            respuesta_usuario = input("Tu respuesta: ").strip().upper()
            
            # Limpiar la entrada (separar por comas y quitar espacios)
            seleccion = [r.strip() for r in respuesta_usuario.split(',')]
            
            # Validar que ingresó letras correctas y la cantidad correcta
            if all(r in letras[:len(opciones)] for r in seleccion):
                if len(set(seleccion)) == len(respuestas_correctas):
                    entrada_valida = True
                else:
                    print(f"Debes seleccionar exactamente {len(respuestas_correctas)} opciones diferentes.")
            else:
                print("Entrada no válida. Asegúrate de usar las letras correspondientes.")
                
        # Convertir letras seleccionadas a índices
        indices_usuario = sorted([letras.index(r) for r in seleccion])
        respuestas_correctas_ordenadas = sorted(respuestas_correctas)
        
        # Evaluar respuesta
        if indices_usuario == respuestas_correctas_ordenadas:
            print("\n✅ ¡Correcto!")
            puntaje += 1
        else:
            print("\n❌ Incorrecto.")
            print("Las respuestas correctas eran:")
            for idx in respuestas_correctas_ordenadas:
                print(f"  {letras[idx]}) {opciones[idx]}")
            
            # Mostrar la explicación para estudiar
            if "explicacion" in q and q["explicacion"]:
                print(f"\n💡 Explicación: {q['explicacion']}")
                
        print("-" * 60)

    # Resultados
    print("="*60)
    print(f" RESULTADO FINAL: {puntaje} / {total_preguntas}")
    porcentaje = (puntaje / total_preguntas) * 100
    print(f" PORCENTAJE: {porcentaje:.2f}%")
    print("="*60)

if __name__ == "__main__":
    realizar_prueba()