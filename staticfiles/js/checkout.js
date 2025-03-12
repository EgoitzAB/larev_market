document.addEventListener('DOMContentLoaded', function() {
    // Obtén todos los botones de eliminar dirección
    const eliminarBtns = document.querySelectorAll('.eliminar-btn');

    // Recorre todos los botones y agrega un evento para cada uno
    eliminarBtns.forEach(function(btn) {
        btn.addEventListener('click', function(event) {
            event.preventDefault();  // Evita el comportamiento por defecto

            // Obtén el ID de la dirección desde el atributo data-id
            const direccionId = btn.getAttribute('data-id');
            const direccionItem = document.getElementById('direccion-' + direccionId);

            // Realiza la solicitud de eliminación
            fetch('/checkout/eliminar_direccion/' + direccionId + '/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    // Aquí podemos agregar más datos si es necesario
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    direccionItem.remove();  // Eliminar el elemento de la lista
                }
            })
            .catch(error => {
            });
        });
    });
});
