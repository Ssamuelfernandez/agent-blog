"""Agente único con límite de pasos que usa las herramientas del servidor MCP."""
import asyncio
import json
import os
from mcp import Client
from ollama import chat

MODELO = os.getenv("OLLAMA_MODEL", "qwen3.5:4b")
URL_MCP = os.getenv("MCP_URL", "http://127.0.0.1:8001/mcp")
REGLAS = (
    "Eres el ayudante de un blog de cocina donde compartir una receta "
    "es tan fácil como contarla. Las recetas son sencillas: a partir del "
    "nombre o la idea del usuario, completa tú el título, una descripción "
    "breve, los ingredientes con cantidades y los pasos usando tu "
    "conocimiento culinario. No hagas preguntas: no pidas más datos ni "
    "autor, que por defecto es admin. Antes de crear un borrador, consulta "
    "las recetas publicadas para no duplicar una existente. Escribe los "
    "ingredientes y los pasos de forma clara y breve, uno por línea, para "
    "que se lean de un vistazo mientras se cocina. Puedes crear como "
    "máximo un borrador, nunca publicar ni borrar."
)


def a_herramienta_ollama(herramienta) -> dict:
    """Convierte una herramienta MCP al formato de herramientas de Ollama."""
    return {
        "type": "function",
        "function": {
            "name": herramienta.name,
            "description": herramienta.description or "",
            "parameters": herramienta.input_schema,
        },
    }


def leer_resultado(resultado):
    """Extrae el dato de la respuesta MCP o lanza el error que devuelva."""
    if resultado.is_error:
        texto = " ".join(getattr(c, "text", "") for c in resultado.content)
        raise RuntimeError(texto or "Error en la herramienta")
    datos = resultado.structured_content
    if datos is None:
        texto = "".join(getattr(c, "text", "") for c in resultado.content)
        return json.loads(texto) if texto else None
    if list(datos) == ["result"]:
        return datos["result"]
    return datos


async def ejecutar(encargo: str) -> None:
    mensajes = [
        {"role": "system", "content": REGLAS},
        {"role": "user", "content": encargo},
    ]
    consultado = False
    guardado = False
    async with Client(URL_MCP) as cliente:
        herramientas = (await cliente.list_tools()).tools
        permitidas = {h.name for h in herramientas}
        for _ in range(6):
            respuesta = chat(
                model=MODELO,
                messages=mensajes,
                tools=[a_herramienta_ollama(h) for h in herramientas],
            )
            mensajes.append(respuesta.message)
            llamadas = respuesta.message.tool_calls or []
            if not llamadas:
                print(respuesta.message.content or "Sin respuesta final del modelo")
                return
            for llamada in llamadas:
                nombre = llamada.function.name
                argumentos = llamada.function.arguments
                try:
                    if nombre not in permitidas:
                        raise ValueError("Herramienta no autorizada")
                    if nombre == "crear_borrador" and not consultado:
                        raise ValueError("Consulta articulos antes de guardar")
                    if nombre == "crear_borrador" and guardado:
                        raise ValueError("Ya se ha creado un borrador")
                    if not isinstance(argumentos, dict):
                        raise ValueError("Argumentos no validos")
                    resultado = leer_resultado(
                        await cliente.call_tool(nombre, argumentos)
                    )
                    if nombre == "listar_articulos":
                        consultado = True
                    if nombre == "crear_borrador":
                        guardado = True
                except Exception as error:
                    resultado = {"error": type(error).__name__, "detalle": str(error)}
                print("Herramienta:", nombre, "->", resultado)
                mensajes.append({
                    "role": "tool",
                    "tool_name": nombre,
                    "content": json.dumps(resultado, ensure_ascii=False),
                })
    print("Detenido: máximo de seis ciclos alcanzado")

if __name__ == "__main__":
    asyncio.run(ejecutar(input("Cuéntame tu receta:")))
