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

    function applyFilters(table) {
        var textInput = document.querySelector('.report-filter[data-filter-for="' + table.id + '"]');
        var schoolSelect = document.querySelector('.report-school-filter[data-filter-for="' + table.id + '"]');
        var query = textInput ? textInput.value.toLowerCase() : '';
        var school = schoolSelect ? schoolSelect.value : '';
        var schoolCols = (schoolSelect && schoolSelect.getAttribute('data-school-cols'))
            ? schoolSelect.getAttribute('data-school-cols').split(',').map(Number)
            : [];
        var year = table.getAttribute('data-year-filter');

        var rows = table.querySelectorAll('tbody tr');
        rows.forEach(function (row) {
            var matchesText = !query || row.textContent.toLowerCase().indexOf(query) !== -1;
            var matchesSchool = !school || schoolCols.some(function (colIndex) {
                var cell = row.children[colIndex];
                return cell && cell.textContent.trim() === school;
            });
            var matchesYear = !year || row.getAttribute('data-season') === year;
            row.style.display = (matchesText && matchesSchool && matchesYear) ? '' : 'none';
        });
    }

    function getYearFromHash() {
        var match = /^#year-(\d+)$/.exec(location.hash);
        return match ? match[1] : null;
    }

    function applyYearHashFilter() {
        var year = getYearFromHash();
        if (!year) return;
        document.querySelectorAll('table.sortable-table').forEach(function (table) {
            if (!table.querySelector('tbody tr[data-season]')) return;
            table.setAttribute('data-year-filter', year);
            applyFilters(table);
            var firstMatch = table.querySelector('tbody tr[data-season="' + year + '"]');
            if (firstMatch) firstMatch.scrollIntoView({ block: 'center' });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('table.sortable-table').forEach(makeSortable);
        document.querySelectorAll('.report-filter[data-filter-for]').forEach(function (input) {
            var table = document.getElementById(input.getAttribute('data-filter-for'));
            if (table) input.addEventListener('input', function () { applyFilters(table); });
        });
        document.querySelectorAll('.report-school-filter[data-filter-for]').forEach(function (select) {
            var table = document.getElementById(select.getAttribute('data-filter-for'));
            if (table) select.addEventListener('change', function () { applyFilters(table); });
        });
        applyYearHashFilter();
    });

    window.addEventListener('hashchange', applyYearHashFilter);
})();
