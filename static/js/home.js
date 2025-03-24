document.addEventListener("DOMContentLoaded", function () {
    const precioSpan = document.getElementById("precio-seleccionado");
    const pesoSpan = document.getElementById("peso-seleccionado");

    if (!precioSpan || !pesoSpan) {
        console.error("No se encontraron los elementos de precio o peso en el DOM.");
        return;
    }

    const radios = document.querySelectorAll("input[name='variante_id']");
    
    radios.forEach(radio => {
        radio.addEventListener("change", function () {
            precioSpan.textContent = "€" + this.dataset.precio;
            pesoSpan.textContent = this.dataset.peso + "g";
        });
    });
});
