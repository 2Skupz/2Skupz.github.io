"""
Shared writer for standalone report pages: one or more sortable/filterable
HTML tables, styled to match the main championship page.
"""
import html as htmlmod
import re
from datetime import datetime


def dateSortKey(dateStr):
    """Convert a 'Mon D, YYYY' date string into a YYYYMMDD integer for sorting."""
    try:
        return int(datetime.strptime(dateStr.strip(), '%b %d, %Y').strftime('%Y%m%d'))
    except ValueError:
        return 0


class Html(str):
    """A string that is already-rendered HTML and should not be re-escaped."""
    pass


def schoolSlug(name):
    """Turn a school name into a filesystem/URL-safe slug for its detail page."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def schoolHref(name, fromDir='reports'):
    """
    Build a relative href to a school's detail page.

    fromDir describes where the linking page lives:
        'reports' - data/reports/*.html (e.g. schoolBySchool.html, allBouts.html)
        'web'     - web/*.html (e.g. cfbHeavyweights.html)
        'school'  - data/reports/schools/*.html (linking to another school page)
    """
    slug = schoolSlug(name)
    if fromDir == 'reports':
        return f'schools/{slug}.html'
    if fromDir == 'web':
        return f'../data/reports/schools/{slug}.html'
    if fromDir == 'school':
        return f'{slug}.html'
    raise ValueError(f'Unknown fromDir: {fromDir}')


def schoolLink(name, fromDir='reports'):
    """Return an <a> tag (as Html) linking a school's name to its detail page."""
    href = schoolHref(name, fromDir)
    safeName = htmlmod.escape(str(name))
    return Html(f'<a class="school-link" href="{href}">{safeName}</a>')


def formatBoutHTML(game, teamName, fromDir='reports', linkTeams=True):
    """
    Format a bout as an HTML list item with `teamName` written first and the
    line color-coded by result (win/loss/tie). Both team names link to their
    school detail pages unless linkTeams is False.
    """
    if game.teamA == teamName:
        team, opponent, teamScore, oppScore = game.teamA, game.teamB, game.scoreA, game.scoreB
    else:
        team, opponent, teamScore, oppScore = game.teamB, game.teamA, game.scoreB, game.scoreA

    if teamScore > oppScore:
        resultClass = "result-win"
    elif teamScore < oppScore:
        resultClass = "result-loss"
    else:
        resultClass = "result-tie"

    teamHtml = schoolLink(team, fromDir) if linkTeams else htmlmod.escape(team)
    opponentHtml = schoolLink(opponent, fromDir) if linkTeams else htmlmod.escape(opponent)

    return (
        f'<li class="{resultClass}"><span class="bout-date">{game.date}</span> '
        f'<span class="bout-team">{teamHtml}</span> {teamScore}:{oppScore} {opponentHtml}</li>'
    )


def _cell(value):
    if isinstance(value, tuple) and len(value) == 2:
        display, sortKey = value
        displayHtml = display if isinstance(display, Html) else htmlmod.escape(str(display))
        return f'<td data-sort="{htmlmod.escape(str(sortKey))}">{displayHtml}</td>'
    if isinstance(value, Html):
        return f'<td>{value}</td>'
    return f'<td>{htmlmod.escape(str(value))}</td>'


def _cellText(value):
    """Plain-text form of a cell value, for building the school filter's option list."""
    if isinstance(value, tuple) and len(value) == 2:
        value = value[0]
    text = re.sub(r'<[^>]+>', '', str(value))
    return htmlmod.unescape(text).strip()


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
            rowAttrs (list[dict], optional): one dict of extra HTML attributes
                per row (same order/length as rows), e.g. {'data-season': 1937}
            schoolFilterCols (list[int], optional): column indexes containing
                school names. When given, a "Filter by school" dropdown is
                added alongside the text filter, populated with the exact
                school names found in those columns, so e.g. selecting
                "Washington" shows only bouts naming that exact school and
                not "Washington State" or "Washington & Lee".
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
        rowAttrs = section.get('rowAttrs')
        schoolFilterCols = section.get('schoolFilterCols')
        tableId = f'table-{i}'

        heading = section.get('heading')
        if heading:
            parts.append(f'        <h2>{htmlmod.escape(heading)}</h2>\n')

        parts.append('        <div class="filter-row">\n')
        parts.append(
            f'            <input type="text" class="report-filter" '
            f'placeholder="Filter..." data-filter-for="{tableId}">\n'
        )
        if schoolFilterCols:
            schools = sorted({
                _cellText(row[col]) for row in rows for col in schoolFilterCols
            })
            colsAttr = ','.join(str(c) for c in schoolFilterCols)
            parts.append(
                f'            <select class="report-school-filter" '
                f'data-filter-for="{tableId}" data-school-cols="{colsAttr}">\n'
            )
            parts.append('                <option value="">All Schools</option>\n')
            for school in schools:
                safeSchool = htmlmod.escape(school)
                parts.append(f'                <option value="{safeSchool}">{safeSchool}</option>\n')
            parts.append('            </select>\n')
        parts.append('        </div>\n')
        parts.append(f'        <table class="sortable-table" id="{tableId}">\n')
        parts.append('            <thead>\n                <tr>\n')
        for colIdx, headerText in enumerate(headers):
            dataType = 'number' if colIdx in numericCols else 'text'
            parts.append(
                f'                    <th data-type="{dataType}">'
                f'{htmlmod.escape(headerText)}<span class="sort-arrow"></span></th>\n'
            )
        parts.append('                </tr>\n            </thead>\n            <tbody>\n')

        for rowIdx, row in enumerate(rows):
            attrHtml = ''
            if rowAttrs:
                attrHtml = ''.join(
                    f' {name}="{htmlmod.escape(str(val))}"'
                    for name, val in rowAttrs[rowIdx].items()
                )
            parts.append(f'                <tr{attrHtml}>\n')
            for value in row:
                parts.append('                    ' + _cell(value) + '\n')
            parts.append('                </tr>\n')

        parts.append('            </tbody>\n        </table>\n')

    parts.append(f'    </div>\n    <script src="{jsPath}"></script>\n</body>\n</html>\n')

    outputFile.parent.mkdir(parents=True, exist_ok=True)
    with open(outputFile, 'w') as f:
        f.write(''.join(parts))


def writeSchoolDetailPage(team, outputDir):
    """
    Write a standalone detail page for one school: its overall record, every
    reign it has held, and every bout it has fought as a challenger.

    Args:
        team: a Team object (see models.heavyweightClasses)
        outputDir: directory to write the page into (SCHOOL_REPORTS_DIR)
    """
    name = htmlmod.escape(team.name)
    cW, cL, cT, dW, dL, dT, numReigns, natties = team.records()

    parts = [f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} — Belt History</title>
    <link rel="stylesheet" href="../../../web/assets/cfbHeavyweights.css">
</head>
<body>
    <div class="report-page">
        <a class="back-link" href="../../../web/cfbHeavyweights.html">&larr; Back to Championship Page</a>
        <a class="back-link" href="../schoolBySchool.html">&larr; Back to School Reports</a>
        <h1>{name}</h1>
        <div class="small-table-container">
            <div class="champ-header">Belt History</div>
            <div class="text-content">
                <table class="table">
                    <tr>
                        <th>Number of Reigns</th>
                        <td>{numReigns}</td>
                    </tr>
                    <tr>
                        <th>National Titles</th>
                        <td>{f"{natties} — ({team.getTitleString()})" if natties else "0"}</td>
                    </tr>
                    <tr>
                        <th>Record in Bouts</th>
                        <td>{dW+cW}-{dL+cL}-{dT+cT}</td>
                    </tr>
                    <tr>
                        <th>As Belt Holder</th>
                        <td>{dW}-{dL}-{dT}</td>
                    </tr>
                    <tr>
                        <th>As Challenger</th>
                        <td>{cW}-{cL}-{cT}</td>
                    </tr>
                </table>
            </div>
        </div>
"""]

    if team.currentReign is not None:
        reignLength = len(team.currentReign.games)
        gs = "game" if reignLength == 1 else "games"
        parts.append('<div class="content-section">\n')
        parts.append('    <h3>***Current Reign***</h3>\n')
        parts.append(f'    <p>{reignLength} {gs}</p>\n')
        parts.append('    <ul>\n')
        for game in team.currentReign.games:
            parts.append(f'        {formatBoutHTML(game, team.name, fromDir="school")}\n')
        parts.append('    </ul>\n</div>\n\n')

    if team.reigns:
        parts.append('<div class="content-section">\n')
        parts.append('    <h3>Previous Reigns:</h3>\n')
        numReignsLabel = len(team.reigns)
        for reign in reversed(team.reigns):
            parts.append(f'    <h4>Reign #{numReignsLabel}</h4>\n')
            parts.append('    <ul>\n')
            for game in reign.games:
                parts.append(f'        {formatBoutHTML(game, team.name, fromDir="school")}\n')
            parts.append('    </ul>\n')
            numReignsLabel -= 1
        parts.append('</div>\n\n')

    numChall = len(team.challenges)
    gs = "time" if numChall == 1 else "times"
    parts.append('<div class="content-section">\n')
    parts.append('    <h3>Challenges:</h3>\n')
    parts.append(f'    <p>{name} has challenged {numChall} {gs}, winning {numReigns}:</p>\n')
    parts.append('    <ul>\n')
    for game in team.challenges:
        parts.append(f'        {formatBoutHTML(game, team.name, fromDir="school")}\n')
    parts.append('    </ul>\n</div>\n\n')

    parts.append('    </div>\n</body>\n</html>\n')

    outputDir.mkdir(parents=True, exist_ok=True)
    outputFile = outputDir / f'{schoolSlug(team.name)}.html'
    with open(outputFile, 'w') as f:
        f.write(''.join(parts))
