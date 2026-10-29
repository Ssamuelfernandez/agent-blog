"""Servidor MCP"""
from mcp.server import MCPServer
from herramientas import listar_articulos as obtener_publicados
from herramientas import crear_borrador as guardar_borrador

mcp = MCPServer("Blog de cocina")

@mcp.tool()
def listar_articulos() -> list[dict]:
    """Lista las recetas publicadas del blog de cocina."""
    return obtener_publicados()

@mcp.tool()
def crear_borrador(
    titulo: str,
    ingredientes: str,
    pasos: str,
    descripcion: str = "",
    autor: str = "admin",
) -> dict:
    """Crea una receta como borrador NO publicado desde datos proporcionados."""
    return guardar_borrador(titulo, ingredientes, pasos, descripcion, autor)

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8001)
