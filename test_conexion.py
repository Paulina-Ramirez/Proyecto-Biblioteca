from app.config.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM Libros"))
        print(f"Conexion exitosa. Libros en la BD: {result.scalar()}")
except Exception as e:
    print(f"Error: {e}")