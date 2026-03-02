document.addEventListener('DOMContentLoaded', function() {
    var checkbox = document.querySelector('#id_is_class_incharge');
    var fields = document.querySelectorAll('.field-assigned_class, .field-assigned_section, .field-assigned_wing');

    function toggleFields() {
        fields.forEach(function(f) {
            f.style.display = checkbox.checked ? 'block' : 'none';
        });
    }

    if (checkbox) {
        checkbox.addEventListener('change', toggleFields);
        toggleFields(); // Run on page load
    }
});
