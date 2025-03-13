window.addEventListener('scroll', function () {
    var fixedTop = document.querySelector('.fixed-top');
    var scrollPosition = window.scrollY;
    var windowWidth = window.innerWidth;

    if (windowWidth < 992) {
        if (scrollPosition > 55) {
            fixedTop.classList.add('shadow');
        } else {
            fixedTop.classList.remove('shadow');
        }
    } else {
        if (scrollPosition > 55) {
            fixedTop.classList.add('shadow');
            fixedTop.style.top = '-55px';
        } else {
            fixedTop.classList.remove('shadow');
            fixedTop.style.top = '0';
        }
    }
});


document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('age-modal');
    const enterButton = document.getElementById('enter-site');
    const confirmAgeCheckbox = document.getElementById('confirm-age');

    if (modal) {
        enterButton.addEventListener('click', () => {
            if (confirmAgeCheckbox.checked) {
                // Ocultar el modal
                modal.style.display = 'none';

                // Guardar en la sesión del navegador (usando una llamada AJAX)
                fetch('/verificar-edad/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                    body: JSON.stringify({ edad_confirmada: true }),
                });
            } else {
                alert('Por favor, confirma que tienes 18 años o más.');
            }
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    // Función para filtrar productos según la categoría
    function filtrarCategoria(categoriaId) {
        // Filtrar las categorías y mostrar las correspondientes
        const sections = document.querySelectorAll('.category-section');
        if (categoriaId === 'all') {
            sections.forEach(section => section.style.display = 'block');
        } else {
            sections.forEach(section => {
                section.style.display = section.id === categoriaId ? 'block' : 'none';
            });
        }

        // Activar el botón de la categoría seleccionada
        document.querySelectorAll('.category-btn').forEach(button => {
            button.classList.toggle('active', button.dataset.category === categoriaId);
        });
    }

    // Función para ordenar los productos según el criterio seleccionado
    function ordenarProductos() {
        const sortOrder = document.getElementById('sortOrder').value;
        const productGrid = document.querySelector('.product-grid');
        const productCards = Array.from(productGrid.children);

        productCards.sort((a, b) => {
            const priceA = parseFloat(a.querySelector('.variant').dataset.price);
            const priceB = parseFloat(b.querySelector('.variant').dataset.price);
            const nameA = a.querySelector('h3').textContent.trim().toLowerCase();
            const nameB = b.querySelector('h3').textContent.trim().toLowerCase();
            switch (sortOrder) {
                case 'precio_asc':
                    return priceA - priceB;
                case 'precio_desc':
                    return priceB - priceA;
                case 'nombre_asc':
                    return nameA.localeCompare(nameB); // Ordenar de A a Z
                case 'nombre_desc':
                    return nameB.localeCompare(nameA); // Ordenar de Z a A
                case 'novedades':
                    return 0; // Cambiar este valor según tus necesidades.
                case 'popularidad':
                    return 0; // Cambiar este valor según tus necesidades.
                default:
                    return 0;
            }
        });

        productGrid.innerHTML = '';  // Limpiar el contenedor de productos
        productCards.forEach(card => productGrid.appendChild(card));  // Volver a agregar los productos ordenados
    }

    // Establecer eventos para botones de categorías
    document.querySelectorAll('.category-btn').forEach(button => {
        button.addEventListener('click', () => {
            const category = button.dataset.category;
            filtrarCategoria(category);
        });
    });

    // Evento para el cambio de orden
    const sortSelect = document.getElementById('sortOrder');
    sortSelect.addEventListener('change', ordenarProductos);

    // Función inicial de filtrado para la categoría "all"
    filtrarCategoria('all');
});
