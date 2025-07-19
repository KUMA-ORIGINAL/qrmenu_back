// dependent_selects.js
document.addEventListener('DOMContentLoaded', function() {
    var venueSelect = document.getElementById('id_venue');
    var spotSelect = document.getElementById('id_spot');
    var categorySelect = document.getElementById('id_category');

    if (!venueSelect) return;

    venueSelect.addEventListener('change', function() {
        var venueId = this.value;

        fetch(`/admin/ajax/get_spots/?venue_id=${venueId}`)
            .then(response => response.json())
            .then(data => {
                spotSelect.innerHTML = '<option value="">---</option>';
                data.forEach(function(spot) {
                    var opt = document.createElement('option');
                    opt.value = spot.id;
                    opt.innerHTML = spot.name;
                    spotSelect.appendChild(opt);
                });
            });

        fetch(`/admin/ajax/get_categories/?venue_id=${venueId}`)
            .then(response => response.json())
            .then(data => {
                categorySelect.innerHTML = '<option value="">---</option>';
                data.forEach(function(cat) {
                    var opt = document.createElement('option');
                    opt.value = cat.id;
                    opt.innerHTML = cat.category_name;
                    categorySelect.appendChild(opt);
                });
            });
    });
});
