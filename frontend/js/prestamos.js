guard();

if (getMe()) {
    layout("prestamos.html");

    (async function loadLoansPage() {
        try {
            const me = getMe();
            const admin = librarian();

            const [loans, books, users] = await Promise.all([
                api(admin ? "/prestamos/" : `/prestamos/usuario/${me.id_usuario}`),
                api("/libros/"),
                admin ? api("/usuarios/") : Promise.resolve([])
            ]);

            const booksById = Object.fromEntries(
                books.map(book => [book.id_libro, book])
            );
            const usersById = Object.fromEntries(
                users.map(user => [user.id_usuario, user])
            );

            renderLoansPage(loans, booksById, usersById, admin);
        } catch (error) {
            renderLoansError(error);
        }
    })();
}

function renderLoansPage(loans, booksById, usersById, admin) {
    const page = document.querySelector("#page");
    const pageTemplate = document.querySelector("#loans-page-template");
    const fragment = pageTemplate.content.cloneNode(true);

    fragment.querySelector("#loans-title").textContent =
        admin ? "Préstamos" : "Mis préstamos";

    const userHeading = fragment.querySelector("#loan-user-heading");
    userHeading.hidden = !admin;

    const rows = fragment.querySelector("#loans-rows");

    if (loans.length === 0) {
        const emptyFragment = document
            .querySelector("#loans-empty-row-template")
            .content.cloneNode(true);
        const messageCell = emptyFragment.querySelector('[data-field="message"]');
        messageCell.colSpan = admin ? 7 : 6;
        messageCell.textContent = "Sin préstamos registrados.";
        rows.appendChild(emptyFragment);
    } else {
        const rowTemplate = document.querySelector("#loan-row-template");

        loans.forEach(loan => {
            const rowFragment = rowTemplate.content.cloneNode(true);
            const row = rowFragment.querySelector("tr");

            row.querySelector('[data-field="id"]').textContent =
                loan.id_prestamo ?? "";
            const userCell = row.querySelector('[data-field="user"]');
            userCell.hidden = !admin;

            if (admin) {
                userCell.textContent = usersById[loan.id_usuario]?.nombre ?? "";
            }

            row.querySelector('[data-field="book"]').textContent =
                booksById[loan.id_libro]?.titulo ?? "—";
            row.querySelector('[data-field="loan-date"]').textContent =
                fmt(loan.fecha_prestamo);
            row.querySelector('[data-field="due-date"]').textContent =
                fmt(loan.fecha_vencimiento);
            row.querySelector('[data-field="return-date"]').textContent =
                fmt(loan.fecha_devolucion);
            row.querySelector('[data-field="status"]').textContent =
                loan.estado ?? "";

            rows.appendChild(rowFragment);
        });
    }

    page.replaceChildren(fragment);
}

function renderLoansError(error) {
    const page = document.querySelector("#page");
    const fragment = document
        .querySelector("#loans-error-template")
        .content.cloneNode(true);

    fragment.querySelector("#loans-error-message").textContent =
        error?.message ?? "Ocurrió un error al cargar los préstamos.";

    page.replaceChildren(fragment);
}
