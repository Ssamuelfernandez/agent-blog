import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("BLOG_API_URL", "http://127.0.0.1:8000/api/recetas/").rstrip("/") + "/"

def listar_articulos() -> list[dict]:
    """Devuelve articulos publicados del blog."""
    respuesta = requests.get(API_URL, timeout=10)
    respuesta.raise_for_status()
    datos = respuesta.json()
    if isinstance(datos, list):
        return datos
    if isinstance(datos, dict) and isinstance(datos.get("results"), list):
        return datos["results"]
    raise ValueError("La API no devolvio una lista de articulos")

def crear_borrador(
    titulo: str,
    ingredientes: str,
    pasos: str,
    descripcion: str = "",
    autor: str = "admin",
) -> dict:
    """Guarda una receta como borrador NO publicado y devuelve sus datos."""
    autor = autor.strip() or "admin"
    if not all((titulo.strip(), ingredientes.strip(), pasos.strip())):
        raise ValueError("Titulo, ingredientes y pasos no pueden estar vacios")
    token = os.getenv("API_TOKEN", "")
    if not token:
        raise RuntimeError("Falta la variable API_TOKEN")
    respuesta = requests.post(
        API_URL,
        json={
            "titulo": titulo,
            "autor": autor,
            "descripcion": descripcion,
            "ingredientes": ingredientes,
            "pasos": pasos,
        },
        headers={"Authorization": f"Token {token}"},
        timeout=15,
    )
    if respuesta.status_code == 400:
        raise ValueError(f"La API rechazo los datos: {respuesta.text}")
    respuesta.raise_for_status()
    datos = respuesta.json()
    if datos.get("estado") != "borrador":
        raise RuntimeError("La API no ha confirmado el estado borrador")
    return datos