document.addEventListener('DOMContentLoaded', function () {
    const spotSelect = document.querySelector('#id_spot');
    const hallSelect = document.querySelector('#id_hall');

    if (!spotSelect || !hallSelect) return;

    spotSelect.addEventListener('change', function () {
        const spotId = this.value;

        // Очистим "Зал"
        hallSelect.innerHTML = '';

        if (!spotId) {
            const emptyOption = new Option('---------', '');
            hallSelect.appendChild(emptyOption);
            return;
        }

        fetch(`/admin/ajax/get-halls/?spot_id=${spotId}`)
            .then(response => response.json())
            .then(data => {
                hallSelect.innerHTML = '';
                const emptyOption = new Option('---------', '');
                hallSelect.appendChild(emptyOption);

                data.forEach(hall => {
                    const option = new Option(hall.hall_name, hall.id);
                    hallSelect.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Ошибка загрузки залов:', error);
            });
    });

    if (spotSelect.value) {
        const event = new Event('change');
        spotSelect.dispatchEvent(event);
    }
});
