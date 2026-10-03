-- Crear base de datos
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'BibliotecaDB')
BEGIN
    CREATE DATABASE BibliotecaDB;
END
GO

USE BibliotecaDB;
GO

-- ============================================
-- TABLA: Usuarios
-- ============================================
IF OBJECT_ID('Usuarios', 'U') IS NULL
BEGIN
    CREATE TABLE Usuarios (
        id_usuario INT IDENTITY(1,1) PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        rol VARCHAR(20) NOT NULL CHECK (rol IN ('Estudiante', 'Docente', 'Bibliotecario')),
        activo BIT DEFAULT 1,
        fecha_registro DATETIME DEFAULT GETDATE()
    );
END
GO

-- ============================================
-- TABLA: Libros
-- ============================================
IF OBJECT_ID('Libros', 'U') IS NULL
BEGIN
    CREATE TABLE Libros (
        id_libro INT IDENTITY(1,1) PRIMARY KEY,
        isbn VARCHAR(20) UNIQUE NOT NULL,
        titulo VARCHAR(200) NOT NULL,
        autor VARCHAR(150) NOT NULL,
        categoria VARCHAR(80),
        stock_total INT NOT NULL DEFAULT 0 CHECK (stock_total >= 0),
        stock_disponible INT NOT NULL DEFAULT 0 CHECK (stock_disponible >= 0),
        fecha_registro DATETIME DEFAULT GETDATE()
    );
END
GO

-- ============================================
-- TABLA: Prestamos
-- ============================================
IF OBJECT_ID('Prestamos', 'U') IS NULL
BEGIN
    CREATE TABLE Prestamos (
        id_prestamo INT IDENTITY(1,1) PRIMARY KEY,
        id_usuario INT NOT NULL,
        id_libro INT NOT NULL,
        fecha_prestamo DATETIME DEFAULT GETDATE(),
        fecha_vencimiento DATETIME NOT NULL,
        fecha_devolucion DATETIME NULL,
        estado VARCHAR(20) DEFAULT 'Activo' CHECK (estado IN ('Activo', 'Devuelto', 'Vencido')),
        FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
        FOREIGN KEY (id_libro) REFERENCES Libros(id_libro)
    );
END
GO

-- ============================================
-- TABLA: Sanciones
-- ============================================
IF OBJECT_ID('Sanciones', 'U') IS NULL
BEGIN
    CREATE TABLE Sanciones (
        id_sancion INT IDENTITY(1,1) PRIMARY KEY,
        id_usuario INT NOT NULL,
        id_prestamo INT NOT NULL,
        monto DECIMAL(10,2) DEFAULT 0,
        dias_retraso INT DEFAULT 0,
        pagada BIT DEFAULT 0,
        fecha_sancion DATETIME DEFAULT GETDATE(),
        FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
        FOREIGN KEY (id_prestamo) REFERENCES Prestamos(id_prestamo)
    );
END
GO

-- ============================================
-- DATOS DE PRUEBA
-- ============================================
DELETE FROM Sanciones;
DELETE FROM Prestamos;
DELETE FROM Libros;
DELETE FROM Usuarios;
DBCC CHECKIDENT ('Usuarios', RESEED, 0);
DBCC CHECKIDENT ('Libros', RESEED, 0);
GO

INSERT INTO Usuarios (nombre, email, password_hash, rol) VALUES
('Admin Bibliotecario', 'admin@biblio.com', 'hash123', 'Bibliotecario'),
('Juan Docente', 'juan@biblio.com', 'hash123', 'Docente'),
('Maria Estudiante', 'maria@biblio.com', 'hash123', 'Estudiante');
GO

INSERT INTO Libros (isbn, titulo, autor, categoria, stock_total, stock_disponible) VALUES
('978-0132350884', 'Clean Code', 'Robert C. Martin', 'Programación', 5, 5),
('978-0134685991', 'Effective Java', 'Joshua Bloch', 'Programación', 3, 3),
('978-0061120084', 'Cien Años de Soledad', 'Gabriel García Márquez', 'Novela', 4, 4),
('978-0451524935', '1984', 'George Orwell', 'Novela', 2, 2),
('978-0131103627', 'The C Programming Language', 'Kernighan & Ritchie', 'Programación', 3, 3),
('978-0307474728', 'El Amor en los Tiempos del Cólera', 'Gabriel García Márquez', 'Novela', 2, 2),
('978-0201633610', 'Design Patterns', 'Erich Gamma', 'Programación', 1, 1),
('978-8478884452', 'Harry Potter y la Piedra Filosofal', 'J.K. Rowling', 'Fantasía', 6, 6),
('978-0156012195', 'El Principito', 'Antoine de Saint-Exupéry', 'Infantil', 5, 5),
('978-8498382549', 'Sapiens', 'Yuval Noah Harari', 'Historia', 3, 3);
GO

PRINT 'Base de datos BibliotecaDB creada con datos de prueba.';
GO
