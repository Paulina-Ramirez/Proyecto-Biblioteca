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
                
                page.replaceChildren(pageTemplate.content.cloneNode(true));

                // Agregar columna de Acciones al encabezado de la tabla
                const theadTr = page.querySelector("thead tr");
                const th = document.createElement("th");
                th.textContent = "Acciones";
                theadTr.appendChild(th);

                const rows = $("#users-rows");

                if (!users.length) {
                    const empty = $("#users-empty-row-template").content.cloneNode(true);
                    empty.querySelector("td").colSpan = 6;
                    rows.append(empty);
                    return;
                }

                const fragment = document.createDocumentFragment();

                users.forEach((user) => {
                    const row = $("#user-row-template").content.firstElementChild.cloneNode(true);

                    row.querySelector('[data-field="id"]').textContent = user.id_usuario ?? "";
                    row.querySelector('[data-field="name"]').textContent = user.nombre ?? "";
                    row.querySelector('[data-field="email"]').textContent = user.email ?? "";
                    row.querySelector('[data-field="role"]').textContent = user.rol ?? "";

                    const status = row.querySelector('[data-field="status"]');
                    const active = Boolean(user.activo);
                    status.textContent = active ? "Activo" : "Inactivo";
                    status.classList.add(active ? "ok" : "er");

                    // BOTONES DE ACCIÓN (Cambiar Rol y Dar de Baja)
                    const actionsTd = document.createElement("td");
                    actionsTd.style.display = "flex";
                    actionsTd.style.gap = "5px";

                    const btnRole = document.createElement("button");
                    btnRole.className = "sm";
                    btnRole.textContent = "Cambiar Rol";
                    btnRole.onclick = () => cambiarRol(user.id_usuario, user.rol);
                    
                    const btnBaja = document.createElement("button");
                    btnBaja.className = "sm dng"; // dng = danger (rojo)
                    btnBaja.textContent = active ? "Dar de baja" : "Reactivar";
                    btnBaja.onclick = () => toggleActivo(user.id_usuario, active);
                    
                    actionsTd.appendChild(btnRole);
                    actionsTd.appendChild(btnBaja);
                    row.appendChild(actionsTd);

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

                async function cambiarRol(id, currentRole) {
            const nuevoRol = prompt(`Rol actual: ${currentRole}\n\nIngresa el nuevo rol (Estudiante, Docente, Bibliotecario):`);
            if (!nuevoRol) return;
            
            if (!["Estudiante", "Docente", "Bibliotecario"].includes(nuevoRol)) {
                return alert("Rol no válido. Debes escribir exactamente: Estudiante, Docente o Bibliotecario.");
            }
            try {
                await api(`/usuarios/${id}`, { method: "PUT", body: { rol: nuevoRol } });
                toast("Rol actualizado correctamente");
                setTimeout(() => location.reload(), 1000);
            } catch (error) {
                toast(error.message, true);
            }
        }

        async function toggleActivo(id, isActive) {
            const accion = isActive ? "dar de baja" : "reactivar";
            if (!confirm(`¿Estás seguro de ${accion} a este usuario?`)) return;
            try {
                await api(`/usuarios/${id}`, { method: "PUT", body: { activo: !isActive } });
                toast(`Usuario ${isActive ? "dado de baja" : "reactivado"} correctamente`);
                setTimeout(() => location.reload(), 1000);
            } catch (error) {
                toast(error.message, true);
            }
        }
    }
}