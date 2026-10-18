"use strict";

guard();

if (getMe()) {
    layout("sanciones.html");

    (async function loadFines() {
        const page = $("#page");

        try {
            const me = getMe();
            const admin = librarian();

            const [fines, users] = await Promise.all([
                api(admin ? "/sanciones/" : `/sanciones/usuario/${me.id_usuario}`),
                admin ? api("/usuarios/") : Promise.resolve([])
            ]);

            const usersById = Object.fromEntries(
                users.map(user => [user.id_usuario, user])
            );

            const pageTemplate = $("#fines-page-template");
            const rowTemplate = $("#fine-row-template");
            const emptyTemplate = $("#fine-empty-row-template");

            const view = pageTemplate.content.cloneNode(true);
            view.querySelector('[data-role="page-title"]').textContent =
                admin ? "Sanciones" : "Mis sanciones";

            if (!admin) {
                view.querySelector('[data-role="user-heading"]').remove();
            }

            const rows = view.querySelector('[data-role="fines-rows"]');

            if (fines.length === 0) {
                const emptyRow = emptyTemplate.content.cloneNode(true);
                const cell = emptyRow.querySelector('[data-role="empty-message"]');
                cell.textContent = "No hay sanciones registradas.";
                cell.colSpan = admin ? 7 : 6;
                rows.appendChild(emptyRow);
            } else {
                fines.forEach(fine => {
                    const row = rowTemplate.content.cloneNode(true);
                    const cells = row.querySelectorAll("[data-field]");

                    row.querySelector('[data-field="id"]').textContent = fine.id_sancion;
                    row.querySelector('[data-field="user"]').textContent =
                        usersById[fine.id_usuario]?.nombre || "—";
                    row.querySelector('[data-field="loan"]').textContent = `#${fine.id_prestamo}`;
                    row.querySelector('[data-field="days"]').textContent = fine.dias_retraso;
                    row.querySelector('[data-field="amount"]').textContent =
                        `$${Number(fine.monto).toFixed(2)}`;
                    row.querySelector('[data-field="date"]').textContent = fmt(fine.fecha_sancion);

                    const status = row.querySelector('[data-field="status"]');
                    status.textContent = fine.pagada ? "Pagada" : "Pendiente";
                    status.classList.add(fine.pagada ? "ok" : "er");

                    if (!admin) {
                        row.querySelector('[data-field="user"]').remove();
                    }

                    rows.appendChild(row);
                });
            }

            page.replaceChildren(view);
        } catch (error) {
            const banner = document.createElement("div");
            banner.className = "banner";
            banner.textContent = error.message || "No fue posible cargar las sanciones.";
            page.replaceChildren(banner);
        }
    })();
}
