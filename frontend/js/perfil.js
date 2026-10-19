guard();

if (getMe()) {
    layout("perfil.html");

    (async function loadProfile() {
        const me = getMe();
        const page = $("#page");

        try {
            const loans = await api(`/prestamos/usuario/${me.id_usuario}`);
            const books = await api("/libros/");
            const booksById = Object.fromEntries(books.map(b => [b.id_libro, b]));

            const view = $("#profile-page-template").content.cloneNode(true);
            
            view.querySelector("#profile-avatar").textContent = (me.nombre || "?").substring(0, 2).toUpperCase();
            view.querySelector("#profile-name").textContent = me.nombre;
            view.querySelector("#profile-email").textContent = me.email;
            view.querySelector("#profile-role").textContent = me.rol;

            const rows = view.querySelector("#profile-loans-rows");
            const rowTemplate = $("#profile-loan-row-template");

            if (loans.length === 0) {
                rows.innerHTML = `<tr><td colspan="5" class="empty">Aún no has pedido libros prestados.</td></tr>`;
            } else {
                loans.forEach(loan => {
                    const row = rowTemplate.content.cloneNode(true);
                    row.querySelector('[data-field="book"]').textContent = booksById[loan.id_libro]?.titulo || "—";
                    row.querySelector('[data-field="loan-date"]').textContent = fmt(loan.fecha_prestamo);
                    row.querySelector('[data-field="due-date"]').textContent = fmt(loan.fecha_vencimiento);
                    row.querySelector('[data-field="return-date"]').textContent = fmt(loan.fecha_devolucion);

                    const status = row.querySelector('[data-field="status"]');
                    status.textContent = loan.estado;
                    status.classList.add(loan.estado === "Activo" ? "ok" : loan.estado === "Vencido" ? "er" : "wa");

                    rows.appendChild(row);
                });
            }
            page.replaceChildren(view);
        } catch (error) {
            page.innerHTML = `<div class="banner">Error al cargar perfil: ${error.message}</div>`;
        }
    })();
}