"""Prueba de integracion de las funciones HTTP sin modelo IA."""
from herramientas import listar_articulos, crear_borrador

antes = listar_articulos()
print("Recetas publicadas antes:", len(antes))
creado = crear_borrador(
    titulo="Prueba de tortilla de patatas",
    descripcion="Receta de prueba creada desde las herramientas.",
    ingredientes="4 patatas\n4 huevos\nAceite de oliva\nSal",
    pasos="Fríe las patatas.\nBate los huevos y mézclalos.\nCuaja la tortilla.",
)
assert creado["estado"] == "borrador"
assert creado["autor"] == "admin"
assert all(a["id"] != creado["id"] for a in listar_articulos())
print("Borrador creado:", creado["id"])
print("Comprobación: el borrador no es público")
