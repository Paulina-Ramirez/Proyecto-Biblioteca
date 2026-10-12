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
    def descontar_stock(db: Session, id_libro: int, cantidad: int = 1, commit: bool = True) -> int:
        """
        Descuenta 'cantidad' de stock_disponible con un UPDATE atómico que solo
        se aplica si queda stock suficiente (evita stock negativo y condiciones
        de carrera). Devuelve el número de filas afectadas: 1 si se descontó,
        0 si no había stock suficiente o el libro no existe.
        Con commit=False no confirma, para agrupar con otras operaciones.
        """
        filas = db.query(Libro).filter(
            Libro.id_libro == id_libro,
            Libro.stock_disponible >= cantidad
        ).update(
            {Libro.stock_disponible: Libro.stock_disponible - cantidad},
            synchronize_session=False
        )
        if commit:
            db.commit()
        return filas

    @staticmethod
    def eliminar(db: Session, id_libro: int):
        libro = db.query(Libro).filter(Libro.id_libro == id_libro).first()
        if libro:
            db.delete(libro)
            db.commit()
        return libro

    @staticmethod
    def aumentar_stock(db: Session, id_libro: int, cantidad: int = 1, commit: bool = True) -> int:
        """Aumenta stock_disponible con un UPDATE atómico. Devuelve filas afectadas."""
        filas = db.query(Libro).filter(Libro.id_libro == id_libro).update(
            {Libro.stock_disponible: Libro.stock_disponible + cantidad},
            synchronize_session=False
        )
        if commit:
            db.commit()
        return filas