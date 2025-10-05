window.addEventListener("load", function() {
    if (typeof django !== "undefined" && django.jQuery) {
        const $ = django.jQuery;

        const $buttonType = $('#id_button_type');
        const $sectionWrapper = $('#id_section').closest('.form-row, .form-group, .field-section');
        const $categoryWrapper = $('#id_category').closest('.form-row, .form-group, .field-category');

        function toggleFields() {
            const value = $buttonType.val();

            if (value === 'section') {
                $sectionWrapper.show();
                $categoryWrapper.hide();
                $('#id_category').val('');
            } else if (value === 'category') {
                $sectionWrapper.hide();
                $categoryWrapper.show();
                $('#id_section').val('');
            } else {
                $sectionWrapper.hide();
                $categoryWrapper.hide();
            }
        }

        // Первичное включение логики
        toggleFields();

        // Реакция на смену типа кнопки
        $buttonType.on('change', toggleFields);
    } else {
        console.error("Django jQuery не найден. Проверь, загружен ли django.jQuery в админке.");
    }
});