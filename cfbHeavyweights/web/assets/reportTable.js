(function () {
    function cellValue(cell) {
        var sortValue = cell.getAttribute('data-sort');
        return sortValue !== null ? sortValue : cell.textContent.trim();
    }

    function compareCells(a, b, numeric) {
        if (numeric) {
            var an = parseFloat(a);
            var bn = parseFloat(b);
            an = isNaN(an) ? -Infinity : an;
            bn = isNaN(bn) ? -Infinity : bn;
            return an - bn;
        }
        return a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' });
    }

    function makeSortable(table) {
        var headers = Array.prototype.slice.call(table.querySelectorAll('thead th'));
        headers.forEach(function (th, colIndex) {
            th.addEventListener('click', function () {
                var tbody = table.querySelector('tbody');
                var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
                var numeric = th.getAttribute('data-type') === 'number';
                var asc = th.getAttribute('data-sort-dir') !== 'asc';

                rows.sort(function (r1, r2) {
                    var result = compareCells(
                        cellValue(r1.children[colIndex]),
                        cellValue(r2.children[colIndex]),
                        numeric
                    );
                    return asc ? result : -result;
                });

                headers.forEach(function (h) {
                    h.removeAttribute('data-sort-dir');
                    var arrow = h.querySelector('.sort-arrow');
                    if (arrow) arrow.textContent = '';
                });
                th.setAttribute('data-sort-dir', asc ? 'asc' : 'desc');
                var arrow = th.querySelector('.sort-arrow');
                if (arrow) arrow.textContent = asc ? '▲' : '▼';

                rows.forEach(function (row) { tbody.appendChild(row); });
            });
        });
    }

    function makeFilterable(input, table) {
        input.addEventListener('input', function () {
            var query = input.value.toLowerCase();
            var rows = table.querySelectorAll('tbody tr');
            rows.forEach(function (row) {
                row.style.display = row.textContent.toLowerCase().indexOf(query) === -1 ? 'none' : '';
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('table.sortable-table').forEach(makeSortable);
        document.querySelectorAll('[data-filter-for]').forEach(function (input) {
            var table = document.getElementById(input.getAttribute('data-filter-for'));
            if (table) makeFilterable(input, table);
        });
    });
})();
