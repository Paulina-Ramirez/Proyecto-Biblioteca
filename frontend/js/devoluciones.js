guard();

if (getMe()) {
    layout("devoluciones.html");

    const page = $("#page");
    page.replaceChildren($("#returns-page-template").content.cloneNode(true));

    let currentLoan = null;
    const TARIFA_DIARIA = 5;

    $("#search-loan-btn").addEventListener("click", async () => {
        const id = $("#return-loan-id").value;
        if (!id) return;

        try {
            $("#return-error").textContent = "";
            currentLoan = await api(`/prestamos/${id}`);
            
            const books = await api("/libros/");
            const book = books.find(b => b.id_libro === currentLoan.id_libro);

            $("#detail-book").textContent = book ? book.titulo : `ID ${currentLoan.id_libro}`;
            $("#detail-user").textContent = `Usuario ID ${currentLoan.id_usuario}`;
            $("#detail-due-date").textContent = fmt(currentLoan.fecha_vencimiento);
            
            const today = new Date().toISOString().split("T")[0];
            $("#return-date").value = today;

            $("#loan-details").hidden = false;
            calculateFine();

        } catch (error) {
            $("#loan-details").hidden = true;
            $("#return-error").textContent = "Préstamo no encontrado o ya devuelto.";
        }
    });

    $("#return-date").addEventListener("change", calculateFine);

    function calculateFine() {
        if (!currentLoan) return;

        const returnDate = new Date($("#return-date").value + "T00:00:00");
        const dueDate = new Date(currentLoan.fecha_vencimiento + "T00:00:00");

        const diffTime = returnDate - dueDate;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        const daysLate = Math.max(0, diffDays);
        const amount = daysLate * TARIFA_DIARIA;

        const resultBox = $("#fine-result");
        if (daysLate > 0) {
            resultBox.innerHTML = `<strong>Retraso de ${daysLate} días</strong>.<br> Sanción a generar: <b>$${amount.toFixed(2)}</b>`;
            resultBox.style.color = "var(--error)";
        } else {
            resultBox.innerHTML = `<strong>Sin retraso</strong>. No se generan sanciones.`;
            resultBox.style.color = "var(--ok)";
        }
    }

    $("#confirm-return-btn").addEventListener("click", async () => {
    try {
            $("#return-error").textContent = "";
            
            const url = `/prestamos/devolucion`;

            const body = { 
                id_prestamo: currentLoan.id_prestamo,
                fecha_devolucion: $("#return-date").value 
            };

            await api(url, { method: "POST", body: body });
            
            toast("Devolución registrada con éxito");
            setTimeout(() => location.href = "sanciones.html", 1500);
            
        } catch (error) {
            console.error("Error del Backend:", error.message);
            $("#return-error").textContent = error.message;
        }
    });
}