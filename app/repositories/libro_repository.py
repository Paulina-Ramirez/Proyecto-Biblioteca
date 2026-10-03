from sqlalchemy.orm import Session
from app.models.libro import Libro

class LibroRepository:

    @staticmethod
    def crear(db: Session, isbn: str, titulo: str, autor: str, categoria: str, stock_total: int):
        nuevo = Libro(
            isbn=isbn, titulo=titulo, autor=autor,
            categoria=categoria, stock_total=stock_total,
            stock_disponible=stock_total
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)
        return nuevo

    @staticmethod
    def obtener_por_id(db: Session, id_libro: int):
        return db.query(Libro).filter(Libro.id_libro == id_libro).first()

    @staticmethod
    def obtener_por_isbn(db: Session, isbn: str):
        return db.query(Libro).filter(Libro.isbn == isbn).first()

    @staticmethod
    def listar_todos(db: Session):
        return db.query(Libro).all()

    @staticmethod
    def actualizar_stock(db: Session, id_libro: int, nuevo_stock: int):
        libro = db.query(Libro).filter(Libro.id_libro == id_libro).first()
        if libro:
            libro.stock_disponible = nuevo_stock
            db.commit()
            db.refresh(libro)
        return libro

    @staticmethod
    def eliminar(db: Session, id_libro: int):
        libro = db.query(Libro).filter(Libro.id_libro == id_libro).first()
        if libro:
            db.delete(libro)
            db.commit()
        return libro