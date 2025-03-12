document.addEventListener("DOMContentLoaded", function () {
    // Recuperar los favoritos desde localStorage (si existen)
    let favoritosLocalStorage = JSON.parse(localStorage.getItem('favoritos')) || [];

    // Función para actualizar los iconos de favoritos en la interfaz
    function actualizarIconosFavoritos() {
        document.querySelectorAll(".favorito-btn").forEach((boton) => {
            const varianteId = boton.dataset.varianteId; // ID de la variante del producto
            const icono = boton.querySelector("i"); // Icono dentro del botón

            // Si la variante está en los favoritos de localStorage, se actualiza el icono
            if (favoritosLocalStorage.includes(varianteId)) {
                icono.classList.add("fa-solid", "text-danger");
                icono.classList.remove("fa-regular");
            } else {
                icono.classList.add("fa-regular");
                icono.classList.remove("fa-solid", "text-danger");
            }
        });
    }

    // Inicializar la actualización de los iconos cuando la página se cargue
    actualizarIconosFavoritos();

    // Manejo del clic en el botón de favorito
    document.querySelectorAll(".favorito-btn").forEach((boton) => {
        boton.addEventListener("click", function () {
            const varianteId = boton.dataset.varianteId; // ID de la variante del producto
            const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

            // Hacer la solicitud AJAX para añadir/quitar el favorito
            fetch("/toggle-favorito/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: `variante_id=${varianteId}`,
            })
            .then((response) => response.json())
            .then((data) => {
                // Actualizar el array de favoritos en localStorage
                if (data.added) {
                    favoritosLocalStorage.push(varianteId);
                } else {
                    favoritosLocalStorage = favoritosLocalStorage.filter(id => id !== varianteId);
                }

                // Guardar el estado actualizado de los favoritos en localStorage
                localStorage.setItem('favoritos', JSON.stringify(favoritosLocalStorage));

                // Actualizar los iconos de favoritos en la interfaz
                actualizarIconosFavoritos();
            })
            .catch((error) => {
                console.error("Error en la solicitud AJAX:", error);
            });
        });
    });
});
