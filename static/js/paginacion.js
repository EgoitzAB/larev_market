document.addEventListener('DOMContentLoaded', () => {
    // Función para cargar más productos
    function cargarMasProductos(categoria, pagina) {
        const productGrid = document.querySelector(`#${categoria} .product-grid`);
        if (!productGrid) {
            console.error('No se encontró el contenedor de productos para la categoría:', categoria);
            return;
        }

        // Obtener todos los productos ocultos de la categoría
        const productosOcultos = Array.from(productGrid.querySelectorAll('.product-card.d-none'));

        // Mostrar solo los siguientes 9 productos ocultos
        const productosAMostrar = productosOcultos.slice(0, 9);
        productosAMostrar.forEach(producto => {
            producto.classList.remove('d-none');
        });

        // Actualizar el atributo data-pagina del botón "Ver más"
        const verMasButton = document.querySelector(`#${categoria} .ver-mas-btn`);
        const verMenosButton = document.querySelector(`#${categoria} .ver-menos-btn`);

        if (verMasButton && verMenosButton) {
            verMasButton.setAttribute('data-pagina', pagina + 1);
            verMenosButton.setAttribute('data-pagina', pagina + 1);

            // Mostrar el botón "Ver menos" si hay productos mostrados
            verMenosButton.classList.remove('d-none');

            // Ocultar el botón "Ver más" si no hay más productos para mostrar
            const productosRestantes = productosOcultos.slice(9).length;
            if (productosRestantes === 0) {
                verMasButton.style.display = 'none';
            }
        }
    }

    // Función para ocultar productos (Ver menos)
    function cargarMenosProductos(categoria, pagina) {
        const productGrid = document.querySelector(`#${categoria} .product-grid`);
        if (!productGrid) {
            console.error('No se encontró el contenedor de productos para la categoría:', categoria);
            return;
        }

        // Obtener todos los productos visibles de la categoría
        const productosVisibles = Array.from(productGrid.querySelectorAll('.product-card:not(.d-none)'));

        // Ocultar los últimos 9 productos visibles
        const productosAOcultar = productosVisibles.slice(-9);
        productosAOcultar.forEach(producto => {
            producto.classList.add('d-none');
        });

        // Actualizar el atributo data-pagina del botón "Ver menos"
        const verMasButton = document.querySelector(`#${categoria} .ver-mas-btn`);
        const verMenosButton = document.querySelector(`#${categoria} .ver-menos-btn`);

        if (verMasButton && verMenosButton) {
            verMasButton.setAttribute('data-pagina', pagina - 1);
            verMenosButton.setAttribute('data-pagina', pagina - 1);

            // Mostrar el botón "Ver más" si se ocultaron productos
            verMasButton.style.display = 'inline-block';

            // Ocultar el botón "Ver menos" si no hay más productos para ocultar
            if (pagina === 1) {
                verMenosButton.classList.add('d-none');
            }
        }
    }

    // Establecer eventos para los botones "Ver más" y "Ver menos"
    document.querySelectorAll('.ver-mas-btn').forEach(button => {
        button.addEventListener('click', () => {
            const categoria = button.getAttribute('data-categoria');
            const pagina = parseInt(button.getAttribute('data-pagina'));
            cargarMasProductos(categoria, pagina);
        });
    });

    document.querySelectorAll('.ver-menos-btn').forEach(button => {
        button.addEventListener('click', () => {
            const categoria = button.getAttribute('data-categoria');
            const pagina = parseInt(button.getAttribute('data-pagina'));
            cargarMenosProductos(categoria, pagina);
        });
    });
});