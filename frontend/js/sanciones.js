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

            const usersById = Object.fromEntries(users.map(user => [user.id_usuario, user]));
            const view = $("#fines-page-template").content.cloneNode(true);
            
            view.querySelector('[data-role="page-title"]').textContent = admin ? "Sanciones" : "Mis sanciones";
            if (!admin) view.querySelector('[data-role="user-heading"]').remove();

            if (admin) {
                const theadTr = view.querySelector("thead tr");
                const th = document.createElement("th");
                th.textContent = "Acciones";
                theadTr.appendChild(th);
            }

            const rows = view.querySelector('[data-role="fines-rows"]');

            if (fines.length === 0) {
                const emptyRow = $("#fine-empty-row-template").content.cloneNode(true);
                const cell = emptyRow.querySelector('[data-role="empty-message"]');
                cell.textContent = "No hay sanciones registradas.";
                cell.colSpan = admin ? 8 : 6;
                rows.appendChild(emptyRow);
            } else {
                fines.forEach(fine => {
                    const row = $("#fine-row-template").content.cloneNode(true);
                    
                    row.querySelector('[data-field="id"]').textContent = fine.id_sancion;
                    row.querySelector('[data-field="user"]').textContent = usersById[fine.id_usuario]?.nombre || "—";
                    row.querySelector('[data-field="loan"]').textContent = `#${fine.id_prestamo}`;
                    row.querySelector('[data-field="days"]').textContent = fine.dias_retraso;
                    row.querySelector('[data-field="amount"]').textContent = `$${Number(fine.monto).toFixed(2)}`;
                    row.querySelector('[data-field="date"]').textContent = fmt(fine.fecha_sancion);

                    const status = row.querySelector('[data-field="status"]');
                    status.textContent = fine.pagada ? "Pagada" : "Pendiente";
                    status.classList.add(fine.pagada ? "ok" : "er");

                    if (admin) {
                        const actionCell = document.createElement("td");
                        if (!fine.pagada) {
                            const btn = document.createElement("button");
                            btn.className = "sm";
                            btn.textContent = "Marcar Pagada";
                            // 👇 IMPORTANTE: Le pasamos "fine" (el objeto completo), no solo el ID
                            btn.onclick = () => pagarSancion(fine);
                            actionCell.appendChild(btn);
                        }
                        row.appendChild(actionCell);
                    } else {
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

    async function pagarSancion(fine) {
        if (!confirm("¿Confirmas que se ha recibido el pago de esta sanción?")) return;
        try {
            // Creamos una copia exacta de los datos y forzamos pagada a true
            const bodyCompleto = { 
                id_sancion: fine.id_sancion,
                id_usuario: fine.id_usuario,
                id_prestamo: fine.id_prestamo,
                monto: fine.monto,
                dias_retraso: fine.dias_retraso,
                fecha_sancion: fine.fecha_sancion,
                pagada: true // El backend exige que le mandemos TODO el objeto
            };

            await api(`/sanciones/${fine.id_sancion}/pagar`, { 
                method: "PUT", 
                body: bodyCompleto 
            });
            
            toast("Sanción marcada como pagada");
            location.reload();
        } catch (error) {
            toast(error.message, true);
        }
    }
}