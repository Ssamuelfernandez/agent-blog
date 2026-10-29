
from ollama import chat


# Definimos la herramienta que podrá utilizar el modelo.
def sumar(a: int, b: int) -> int:
    """Suma dos números enteros.

    Args:
        a: Primer sumando.
        b: Segundo sumando.
    """
    return a + b


# Creamos la conversación con el usuario.
mensajes = [
    {
        "role": "user",
        "content": "Usa sumar para calcular 27 + 15"
    }
]

# 1. Enviamos la petición al modelo y le indicamos
#    qué herramientas tiene disponibles.
respuesta = chat(
    model="qwen3.5:4b",
    messages=mensajes,
    tools=[sumar],
)

# 2. Comprobamos que el modelo ha solicitado
#    la ejecución de alguna herramienta.
assert respuesta.message.tool_calls, (
    "El modelo no ha solicitado ninguna herramienta"
)

# Añadimos la respuesta del modelo al historial.
mensajes.append(respuesta.message)

# 3. Procesamos las llamadas a herramientas
#    que ha solicitado el modelo.
for llamada in respuesta.message.tool_calls:

    nombre = llamada.function.name
    argumentos = llamada.function.arguments

    print(f"Herramienta solicitada: {nombre}")
    print(f"Argumentos: {argumentos}")

    # Ejecutamos la función Python correspondiente.
    if nombre == "sumar":
        resultado = sumar(**argumentos)
    else:
        raise ValueError(f"Herramienta desconocida: {nombre}")

    print(f"Resultado de la ejecución: {resultado}")

    # 4. Incorporamos el resultado de la herramienta
    #    al historial de la conversación.
    mensajes.append({
        "role": "tool",
        "tool_name": nombre,
        "content": str(resultado),
    })

# Volvemos a consultar al modelo, ahora con el
# resultado de la herramienta en el historial.
respuesta_final = chat(
    model="qwen3.5:4b",
    messages=mensajes,
)

# Mostramos la respuesta definitiva del modelo.
print(f"\nRespuesta del modelo: {respuesta_final.message.content}")
