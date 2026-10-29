# agent-blog

Agente de IA que crea **borradores de recetas** en un blog de cocina. Usa un modelo local (Ollama) que decide qué herramientas llamar, y un servidor MCP que las ejecuta contra la API REST del blog.

## Cómo funciona

```
agente.py  ──HTTP──▶  servidor_mcp.py  ──▶  herramientas.py  ──▶  API de recetas (Django)
(Ollama + bucle)      (expone las tools)     (requests + token)
```

| Fichero | Qué hace |
|---|---|
| `agente.py` | Cliente MCP. Pasa las herramientas al modelo y ejecuta sus llamadas a través del servidor. Aplica las reglas: consultar antes de crear, un solo borrador y máximo seis ciclos. |
| `servidor_mcp.py` | Servidor MCP. Expone `listar_articulos` y `crear_borrador`. |
| `herramientas.py` | Llamadas HTTP a la API (`GET` y `POST`). Es el único sitio con la URL y el token. |
| `prueba_herramientas.py` | Prueba de integración de las herramientas, sin modelo. |
| `prueba_tool_calling.py` | Ejemplo mínimo de tool calling con Ollama. |

El agente nunca ve el token ni la API: solo puede llamar a las dos herramientas del servidor. No puede publicar ni borrar recetas.

## Requisitos

- Python 3.14 y [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com) con el modelo: `ollama pull qwen3.5:4b`
- La API de recetas en marcha (proyecto Django `sdd-sample-project`)
- Node.js, solo si quieres usar el MCP Inspector

## Configuración

```powershell
uv sync
```

Crea un archivo `.env` en la raíz con el token de un usuario administrador de Django:

```
API_TOKEN=tu_token
```

Variables opcionales: `BLOG_API_URL` (por defecto `http://127.0.0.1:8000/api/recetas/`), `OLLAMA_MODEL`, `MCP_URL`.

## Uso

Necesitas tres terminales.

```powershell
# 1. API de recetas (en la carpeta src del proyecto Django)
python manage.py runserver

# 2. Servidor MCP (en la raíz de agent-blog)
uv run python servidor_mcp.py

# 3. Agente (en la raíz de agent-blog)
uv run python agente.py
```

El agente pregunta `Cuéntame tu receta:`. Escribe una idea simple, como `una receta de gazpacho`. El modelo completa título, ingredientes y pasos, y el borrador se guarda con autor `admin`.

## Pruebas

```powershell
uv run python prueba_herramientas.py     # herramientas contra la API, sin IA
uv run mcp dev servidor_mcp.py           # probar el servidor con el Inspector
```

Cada ejecución de las pruebas crea un borrador real en la base de datos. Se pueden borrar desde el admin de Django.
