document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('#universal-search'); // Apne search input ki ID ye rakhni hai
    const resultsBox = document.querySelector('#search-results-dropdown');

    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value;
            if (query.length > 1) {
                fetch(`/student/search/?q=${query}`)
                    .then(response => response.json())
                    .then(data => {
                        resultsBox.innerHTML = '';
                        resultsBox.style.display = 'block';
                        data.results.forEach(item => {
                            resultsBox.innerHTML += `
                                <a href="${item.url}" class="list-group-item list-group-item-action">
                                    <div class="d-flex justify-content-between">
                                        <strong>${item.name}</strong>
                                        <small class="text-primary">${item.class}</small>
                                    </div>
                                    <small class="text-muted">Roll: ${item.roll}</small>
                                </a>`;
                        });
                    });
            } else {
                resultsBox.style.display = 'none';
            }
        });
    }
});
