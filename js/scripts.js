document.addEventListener('DOMContentLoaded', function () {
    // Mostrar notificación al agregar un cliente
    const addClientForm = document.querySelector('form');
    if (addClientForm) {
        addClientForm.addEventListener('submit', function (event) {
            event.preventDefault();
            alert("¡Cliente agregado exitosamente!");
            addClientForm.submit();
        });
    }

    // Validar formularios en tiempo real
    const inputs = document.querySelectorAll('input[required]');
    inputs.forEach(input => {
        input.addEventListener('invalid', function () {
            input.classList.add('is-invalid');
        });

        input.addEventListener('input', function () {
            if (input.checkValidity()) {
                input.classList.remove('is-invalid');
                input.classList.add('is-valid');
            } else {
                input.classList.remove('is-valid');
            }
        });
    });
});
