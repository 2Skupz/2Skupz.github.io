"""
Shared writer for standalone report pages: one or more sortable/filterable
HTML tables, styled to match the main championship page.
"""
import html as htmlmod
from datetime import datetime


def dateSortKey(dateStr):
    """Convert a 'Mon D, YYYY' date string into a YYYYMMDD integer for sorting."""
    try:
        return int(datetime.strptime(dateStr.strip(), '%b %d, %Y').strftime('%Y%m%d'))
    except ValueError:
        return 0


def _cell(value):
    if isinstance(value, tuple) and len(value) == 2:
        display, sortKey = value
        return f'<td data-sort="{htmlmod.escape(str(sortKey))}">{htmlmod.escape(str(display))}</td>'
    return f'<td>{htmlmod.escape(str(value))}</td>'


def writeHtmlReportPage(outputFile, pageTitle, sections, description=None):
    """
    Write a standalone HTML report page with one or more sortable/filterable tables.

    Args:
        outputFile: Path to write the HTML page to (lives in data/reports/)
        pageTitle: <title> / <h1> text
        sections: list of dicts, each with:
            heading (str, optional): <h2> above this table
            headers (list[str]): column header labels
            rows (list[tuple]): row values; a cell may be a plain value or a
                (display, sortKey) tuple when the sort order shouldn't just
                be the displayed text (e.g. dates)
            numericCols (set[int], optional): column indexes that should sort
                numerically rather than alphabetically
        description: optional paragraph shown under the page title
    """
    cssPath = '../../web/assets/cfbHeavyweights.css'
    jsPath = '../../web/assets/reportTable.js'
    backHref = '../../web/cfbHeavyweights.html'

    parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{htmlmod.escape(pageTitle)}</title>
    <link rel="stylesheet" href="{cssPath}">
</head>
<body>
    <div class="report-page">
        <a class="back-link" href="{backHref}">&larr; Back to Championship Page</a>
        <h1>{htmlmod.escape(pageTitle)}</h1>
"""]
    if description:
        parts.append(f'        <p class="description">{htmlmod.escape(description)}</p>\n')

    for i, section in enumerate(sections):
        headers = section['headers']
        rows = section['rows']
        numericCols = section.get('numericCols', set())
        tableId = f'table-{i}'

        heading = section.get('heading')
        if heading:
            parts.append(f'        <h2>{htmlmod.escape(heading)}</h2>\n')

        parts.append(
            f'        <input type="text" class="report-filter" '
            f'placeholder="Filter..." data-filter-for="{tableId}">\n'
        )
        parts.append(f'        <table class="sortable-table" id="{tableId}">\n')
        parts.append('            <thead>\n                <tr>\n')
        for colIdx, headerText in enumerate(headers):
            dataType = 'number' if colIdx in numericCols else 'text'
            parts.append(
                f'                    <th data-type="{dataType}">'
                f'{htmlmod.escape(headerText)}<span class="sort-arrow"></span></th>\n'
            )
        parts.append('                </tr>\n            </thead>\n            <tbody>\n')

        for row in rows:
            parts.append('                <tr>\n')
            for value in row:
                parts.append('                    ' + _cell(value) + '\n')
            parts.append('                </tr>\n')

        parts.append('            </tbody>\n        </table>\n')

    parts.append(f'    </div>\n    <script src="{jsPath}"></script>\n</body>\n</html>\n')

    outputFile.parent.mkdir(parents=True, exist_ok=True)
    with open(outputFile, 'w') as f:
        f.write(''.join(parts))
