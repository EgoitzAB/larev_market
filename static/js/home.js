document.addEventListener("DOMContentLoaded", function () {
    document.body.addEventListener("change", function (event) {
        if (event.target.matches("input[name='variante_id']")) {
            // Encuentra el contenedor del producto más cercano
            const productCard = event.target.closest(".product-card");
            if (!productCard) return;

            // Busca el precio y peso dentro de este producto
            const precioSpan = productCard.querySelector("#precio-seleccionado");
            const pesoSpan = productCard.querySelector("#peso-seleccionado");

            if (precioSpan && pesoSpan) {
                precioSpan.textContent = "€" + event.target.dataset.precio;
                pesoSpan.textContent = event.target.dataset.peso + "g";
            }
        }
    });
});
