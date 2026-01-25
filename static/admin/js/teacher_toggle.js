document.addEventListener('DOMContentLoaded', function() {
    var checkbox = document.querySelector('#id_is_class_teacher');
    var fields = document.querySelector('.field-assigned_class, .field-assigned_section, .field-assigned_wing');
    
    function toggleFields() {
        if (checkbox.checked) {
            fields.style.display = 'block';
        } else {
            fields.style.display = 'none';
        }
    }
    
    if (checkbox) {
        checkbox.addEventListener('change', toggleFields);
        toggleFields(); // Initial state
    }
});
