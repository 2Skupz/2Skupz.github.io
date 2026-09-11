"""
Maps Massey Ratings' raw FBS team names (as used by the KPI project) to the
team name spellings already established across cfbHeavyweights' 1869-present
historical data. Team matching elsewhere in this project is exact-string, so
any Massey name not listed here is assumed to already match.
"""

MASSEY_TO_HEAVYWEIGHTS = {
    "Kent": "Kent State",
    "Ball St": "Ball State",
    "Texas St": "Texas State",
    "Missouri St": "Missouri State",
    "ULM": "Louisiana-Monroe",
    "FL Atlantic": "Florida Atlantic",
    "Miami OH": "Miami (OH)",
    "Fresno St": "Fresno State",
    "N Illinois": "Northern Illinois",
    "WKU": "Western Kentucky",
    "C Michigan": "Central Michigan",
    "Jacksonville St": "Jacksonville State",
    "San Jose St": "San Jose State",
    "Oklahoma St": "Oklahoma State",
    "Washington St": "Washington State",
    "Oregon St": "Oregon State",
    "Florida Intl": "Florida Int'l",
    "Arkansas St": "Arkansas State",
    "New Mexico St": "New Mexico State",
    "Boise St": "Boise State",
    "Coastal Car": "Coastal Carolina",
    "Sam Houston St": "Sam Houston",
    "W Michigan": "Western Michigan",
    "CS Sacramento": "Sacramento State",
    "Appalachian St": "Appalachian State",
    "Arizona St": "Arizona State",
    "Ga Southern": "Georgia Southern",
    "Georgia St": "Georgia State",
    "Iowa St": "Iowa State",
    "Kansas St": "Kansas State",
    "Kennesaw": "Kennesaw State",
    "MTSU": "Middle Tennessee",
    "San Diego St": "San Diego State",
    "UT San Antonio": "UTSA",
    "Utah St": "Utah State",
    "Mississippi": "Ole Miss",
    "Florida St": "Florida State",
    "E Michigan": "Eastern Michigan",
    "Michigan St": "Michigan State",
    "Miami FL": "Miami",
    "Colorado St": "Colorado State",
    "N Dakota St": "North Dakota State",
    "Penn St": "Penn State",
    "Pittsburgh": "Pitt",
    "Mississippi St": "Mississippi State",
    "Ohio St": "Ohio State",
}


def toHeavyweightsName(masseyName):
    """Translate a raw Massey team name to cfbHeavyweights' canonical spelling."""
    return MASSEY_TO_HEAVYWEIGHTS.get(masseyName, masseyName)
