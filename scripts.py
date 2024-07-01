import sqlite3

# Conectar a la base de datos (o crearla si no existe)
conn = sqlite3.connect("stock.db")
cursor = conn.cursor()

# Consulta para crear la tabla
cursor.execute("""
    CREATE TABLE IF NOT EXISTS proveedor (
        id INTEGER PRIMARY KEY,
        nombre VARCHAR(255),
        cuit VARCHAR(20),
        descuento INTEGER,
        ganancia INTEGER
    )
""")

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()
