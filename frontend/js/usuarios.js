guard();

if (getMe()) {
    if (!librarian()) {
        location.href = "dashboard.html";
    } else {
        layout("usuarios.html");

        (async function loadUsers() {
            const page = $("#page");

            try {
                const users = await api("/usuarios/");
                const pageTemplate = $("#users-page-template");
                const rowTemplate = $("#user-row-template");
                const emptyTemplate = $("#users-empty-row-template");

                page.replaceChildren(pageTemplate.content.cloneNode(true));

                const rows = $("#users-rows");

                if (!users.length) {
                    rows.append(emptyTemplate.content.cloneNode(true));
                    return;
                }

                const fragment = document.createDocumentFragment();

                users.forEach((user) => {
                    const row = rowTemplate.content.firstElementChild.cloneNode(true);

                    row.querySelector('[data-field="id"]').textContent = user.id_usuario ?? "";
                    row.querySelector('[data-field="name"]').textContent = user.nombre ?? "";
                    row.querySelector('[data-field="email"]').textContent = user.email ?? "";
                    row.querySelector('[data-field="role"]').textContent = user.rol ?? "";

                    const status = row.querySelector('[data-field="status"]');
                    const active = Boolean(user.activo);

                    status.textContent = active ? "Activo" : "Inactivo";
                    status.classList.add(active ? "ok" : "er");

                    fragment.append(row);
                });

                rows.append(fragment);
            } catch (error) {
                page.replaceChildren();
                const banner = document.createElement("div");
                banner.className = "banner";
                banner.textContent = error?.message || "No fue posible cargar los usuarios.";
                page.append(banner);
            }
        })();
    }
}
