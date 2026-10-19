guard();

if (getMe()) {
  layout("dashboard.html");

  (async () => {
    try {
      // Se reutilizan únicamente endpoints que ya consume el frontend.
      const me = getMe();
      const [books, loans, fines] = await Promise.all([
        api("/libros/"),
        api(librarian() ? "/prestamos/" : `/prestamos/usuario/${me.id_usuario}`),
        api(librarian() ? "/sanciones/" : `/sanciones/usuario/${me.id_usuario}`)
      ]);

      const page = $("#page");
      const template = $("#dashboard-template");
      page.replaceChildren(template.content.cloneNode(true));

      const setText = (selector, value) => {
        const element = page.querySelector(selector);
        if (element) element.textContent = String(value ?? "");
      };

      const isLibrarian = librarian();
      const activeLoans = loans.filter(item => item.estado === "Activo").length;
      const pendingFines = fines.filter(item => !item.pagada).length;
      const availableCopies = books.reduce(
        (sum, book) => sum + Number(book.stock_disponible || 0), 0
      );

      // Datos de las tarjetas de resumen.
      setText("#dashboard-first-name", (me.nombre || "¡hola!").split(" ")[0]);
      setText("#stat-books", books.length);
      setText("#stat-available", availableCopies);
      setText("#stat-loans", activeLoans);
      setText("#stat-loans-label", isLibrarian ? "Préstamos activos" : "Mis préstamos activos");
      setText("#stat-loans-description", isLibrarian ? "Pendientes de devolución" : "Actualmente a tu cargo");
      setText("#stat-fines", pendingFines);
      setText("#stat-fines-label", isLibrarian ? "Sanciones pendientes" : "Mis sanciones pendientes");
      setText("#quick-loans-title", isLibrarian ? "Gestionar préstamos" : "Mis préstamos");
      setText("#quick-fines-title", isLibrarian ? "Revisar sanciones" : "Mis sanciones");

      // La gráfica se calcula localmente a partir del catálogo existente.
      const categoryCounts = books.reduce((acc, book) => {
        const category = String(book.categoria || "Sin categoría").trim() || "Sin categoría";
        acc[category] = (acc[category] || 0) + 1;
        return acc;
      }, {});
      const categories = Object.entries(categoryCounts).sort((a, b) => b[1] - a[1]);
      const totalCategorized = categories.reduce((sum, [, count]) => sum + count, 0);
      const palette = ["#d77b98", "#a58ac7", "#e8ad8c", "#7fa9c7", "#c6a1b8", "#9cb7a1", "#d7bd79"];
      let running = 0;
      const gradientParts = categories.map(([name, count], index) => {
        const start = running;
        running += totalCategorized ? count / totalCategorized * 100 : 0;
        return `${palette[index % palette.length]} ${start}% ${running}%`;
      });
      const donutGradient = gradientParts.length
        ? `conic-gradient(${gradientParts.join(", ")})`
        : "conic-gradient(#eee7ed 0% 100%)";

      const categoryContent = $("#category-content");
      const categoryEmpty = $("#category-empty");
      const categoryLegend = $("#category-legend");
      if (categories.length) {
        categoryContent.hidden = false;
        categoryEmpty.hidden = true;
        $("#category-donut").style.background = donutGradient;
        $("#category-donut").setAttribute(
          "aria-label",
          `Gráfica de dona con ${categories.length} categorías`
        );
        setText("#donut-total", books.length);

        const legendTemplate = $("#category-legend-template");
        categories.slice(0, 7).forEach(([name, count], index) => {
          const fragment = legendTemplate.content.cloneNode(true);
          const row = fragment.querySelector(".legend-row");
          const dot = fragment.querySelector(".legend-dot");
          const nameElement = fragment.querySelector(".legend-name");
          const countElement = fragment.querySelector(".legend-count");
          const percentElement = fragment.querySelector(".legend-percent");

          dot.style.backgroundColor = palette[index % palette.length];
          nameElement.textContent = name;
          nameElement.title = name;
          countElement.textContent = String(count);
          percentElement.textContent = `${totalCategorized ? Math.round(count / totalCategorized * 100) : 0}%`;
          categoryLegend.appendChild(fragment);
        });
      } else {
        categoryContent.hidden = true;
        categoryEmpty.hidden = false;
        $("#category-footnote").hidden = true;
      }

      // La actividad se limita a datos existentes y se ordena por fecha descendente.
      const recentBooks = books
        .filter(book => book.fecha_registro)
        .map(book => ({
          kind: "book",
          date: new Date(book.fecha_registro),
          title: book.titulo || "Libro sin título",
          detail: `Libro registrado · ${book.categoria || "Sin categoría"}`,
          icon: "♡"
        }));

      const recentLoans = loans
        .filter(loan => loan.fecha_prestamo)
        .map(loan => {
          const book = books.find(item => Number(item.id_libro) === Number(loan.id_libro));
          return {
            kind: "loan",
            date: new Date(loan.fecha_prestamo),
            title: book?.titulo || `Préstamo #${loan.id_prestamo}`,
            detail: loan.estado === "Devuelto"
              ? "Préstamo devuelto"
              : `Préstamo · ${loan.estado || "Registrado"}`,
            icon: "↗"
          };
        });

      const recentActivity = [...recentBooks, ...recentLoans]
        .filter(item => !Number.isNaN(item.date.getTime()))
        .sort((a, b) => b.date - a.date)
        .slice(0, 4);

      const dateLabel = date => {
        const days = Math.floor((Date.now() - date.getTime()) / 86400000);
        if (days <= 0) return "Hoy";
        if (days === 1) return "Ayer";
        if (days < 7) return `Hace ${days} días`;
        return date.toLocaleDateString("es-MX", { day: "numeric", month: "short" });
      };

      const activityList = $("#activity-list");
      if (recentActivity.length) {
        $("#activity-empty").hidden = true;
        activityList.hidden = false;
        const activityTemplate = $("#activity-item-template");

        recentActivity.forEach(item => {
          const fragment = activityTemplate.content.cloneNode(true);
          const icon = fragment.querySelector(".activity-icon");
          icon.classList.add(item.kind === "loan" ? "activity-loan" : "activity-book");
          icon.textContent = item.icon;
          fragment.querySelector(".activity-title").textContent = item.title;
          fragment.querySelector(".activity-detail").textContent = item.detail;
          fragment.querySelector(".activity-date").textContent = dateLabel(item.date);
          fragment.querySelector(".activity-date").dateTime = item.date.toISOString();
          activityList.appendChild(fragment);
        });
      } else {
        $("#activity-empty").hidden = false;
        activityList.hidden = true;
        $("#activity-footnote").hidden = true;
      }
    } catch (error) {
      $("#page").textContent = "";
      const banner = document.createElement("div");
      banner.className = "banner";
      banner.textContent = error.message || "No fue posible cargar el dashboard.";
      $("#page").appendChild(banner);
    }
  })();
}
