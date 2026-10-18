guard();

if (getMe()) {
  layout("libros.html");

  (async () => {
    const categories = ["Programación", "Novela", "Romance", "Fantasía", "Infantil", "Historia"];
    let books = [];

    try {
      books = await api("/libros/");

      const page = $("#page");
      page.replaceChildren($("#books-page-template").content.cloneNode(true));

      const isLibrarian = librarian();
      const heading = $("#books-heading");
      heading.textContent = isLibrarian ? "Libros" : "Catálogo bibliográfico";
      $("#add-book").hidden = !isLibrarian;

      const categoryFilter = $("#category-filter");

      categories.forEach(category => {
        const filterOption = document.createElement("option");
        filterOption.value = category;
        filterOption.textContent = category;
        categoryFilter.appendChild(filterOption);

      });

      const rows = $("#books-rows");

      function draw() {
        const query = $("#book-search").value.trim().toLocaleLowerCase("es-MX");
        const category = categoryFilter.value;
        const availability = $("#availability-filter").value;

        const filteredBooks = books.filter(book => {
          const matchesQuery = !query || [book.titulo, book.autor, book.isbn]
            .some(value => String(value ?? "").toLocaleLowerCase("es-MX").includes(query));
          const matchesCategory = !category || book.categoria === category;
          const matchesAvailability = !availability || Number(book.stock_disponible) > 0;
          return matchesQuery && matchesCategory && matchesAvailability;
        });

        rows.replaceChildren();
        $("#books-count").textContent = String(filteredBooks.length);

        if (!filteredBooks.length) {
          rows.appendChild($("#book-empty-row-template").content.cloneNode(true));
          return;
        }

        filteredBooks.forEach(book => {
          const fragment = $("#book-row-template").content.cloneNode(true);
          fragment.querySelector(".book-title").textContent = book.titulo ?? "Sin título";
          fragment.querySelector(".book-isbn").textContent = book.isbn ?? "—";
          fragment.querySelector(".book-author").textContent = book.autor ?? "—";
          fragment.querySelector(".book-category").textContent = book.categoria || "—";
          fragment.querySelector(".book-stock-total").textContent = String(book.stock_total ?? 0);
          fragment.querySelector(".book-stock-available").textContent = String(book.stock_disponible ?? 0);

          const status = fragment.querySelector(".book-status");
          const available = Number(book.stock_disponible) > 0;
          status.textContent = available ? "Disponible" : "Agotado";
          status.classList.add(available ? "ok" : "er");

          const actions = fragment.querySelector(".book-actions");
          if (isLibrarian) {
            const editButton = document.createElement("button");
            editButton.type = "button";
            editButton.className = "sm";
            editButton.textContent = "Editar";
            editButton.dataset.edit = String(book.id_libro);

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.className = "sm dng";
            deleteButton.textContent = "Eliminar";
            deleteButton.dataset.del = String(book.id_libro);

            actions.append(editButton, document.createTextNode(" "), deleteButton);
          } else {
            const requestButton = document.createElement("button");
            requestButton.type = "button";
            requestButton.className = "sm";
            requestButton.textContent = "Solicitar";
            requestButton.dataset.ask = String(book.id_libro);
            requestButton.disabled = !available;
            actions.appendChild(requestButton);
          }

          rows.appendChild(fragment);
        });
      }

      $("#book-search").addEventListener("input", draw);
      categoryFilter.addEventListener("change", draw);
      $("#availability-filter").addEventListener("change", draw);
      $("#add-book").addEventListener("click", () => openBookForm());
      draw();

      rows.addEventListener("click", async event => {
        const button = event.target.closest("button");
        if (!button) return;

        if (button.dataset.del) {
          if (!confirm("¿Eliminar este libro?")) return;
          try {
            await api("/libros/" + button.dataset.del, { method: "DELETE" });
            toast("Libro eliminado");
            books = await api("/libros/");
            draw();
          } catch (error) {
            toast(error.message, true);
          }
          return;
        }

        if (button.dataset.edit) {
          const book = books.find(item => String(item.id_libro) === button.dataset.edit);
          if (book) openBookForm(book);
          return;
        }

        if (button.dataset.ask) {
          try {
            await api("/prestamos/", {
              method: "POST",
              body: {
                id_usuario: getMe().id_usuario,
                id_libro: Number(button.dataset.ask),
                dias_prestamo: 7
              }
            });
            toast("Solicitud registrada");
            books = await api("/libros/");
            draw();
          } catch (error) {
            toast(error.message, true);
          }
        }
      });

      function openBookForm(book = null) {
        const editing = Boolean(book);
        document.getElementById("book-modal")?.remove();

        const fragment = $("#book-modal-template").content.cloneNode(true);
        const modal = fragment.querySelector("#book-modal");
        const form = fragment.querySelector("#book-form");
        const categorySelect = fragment.querySelector("#book-category");

        // Las opciones se agregan como nodos, no como HTML interpolado.
        categorySelect.replaceChildren();
        categories.forEach(category => {
          const option = document.createElement("option");
          option.value = category;
          option.textContent = category;
          categorySelect.appendChild(option);
        });

        fragment.querySelector("#book-modal-title").textContent =
          editing ? "Editar libro" : "Registrar libro";
        form.elements.isbn.value = book?.isbn ?? "";
        form.elements.titulo.value = book?.titulo ?? "";
        form.elements.autor.value = book?.autor ?? "";
        form.elements.categoria.value = book?.categoria || categories[0];
        form.elements.stock_total.value = String(book?.stock_total ?? 1);

        document.body.appendChild(fragment);
        const activeModal = document.getElementById("book-modal");
        activeModal.querySelector("#cancel-book").addEventListener("click", () => activeModal.remove());
        activeModal.addEventListener("click", event => {
          if (event.target === activeModal) activeModal.remove();
        });

        activeModal.querySelector("#book-form").addEventListener("submit", async event => {
          event.preventDefault();
          const submittedForm = event.currentTarget;
          const formData = Object.fromEntries(new FormData(submittedForm));
          const errorBox = activeModal.querySelector("#book-error");
          errorBox.textContent = "";

          try {
            if (!/^(\d{9}[\dXx]|\d{13})$/.test(formData.isbn.replace(/[-\s]/g, ""))) {
              throw new Error("El ISBN debe tener 10 o 13 caracteres válidos.");
            }
            if (!formData.titulo.trim() || !formData.autor.trim()) {
              throw new Error("Título y autor son obligatorios.");
            }
            if (!Number.isInteger(Number(formData.stock_total)) || Number(formData.stock_total) < 0) {
              throw new Error("El stock debe ser un entero mayor o igual a cero.");
            }

            const body = {
              isbn: formData.isbn.trim(),
              titulo: formData.titulo.trim(),
              autor: formData.autor.trim(),
              categoria: formData.categoria.trim() || null,
              stock_total: Number(formData.stock_total)
            };

            await api(editing ? "/libros/" + book.id_libro : "/libros/", {
              method: editing ? "PUT" : "POST",
              body
            });

            activeModal.remove();
            toast(editing ? "Libro actualizado" : "Libro registrado");
            books = await api("/libros/");
            draw();
          } catch (error) {
            errorBox.textContent = error.message || "No fue posible guardar el libro.";
          }
        });
      }
    } catch (error) {
      const page = $("#page");
      page.replaceChildren();
      const banner = document.createElement("div");
      banner.className = "banner";
      banner.textContent = error.message || "No fue posible cargar el catálogo.";
      page.appendChild(banner);
    }
  })();
}
