Data source: [India Meteorological Department, via IMDWeb](https://imdweb.lwcc.in/).

# Extreme daytime and nighttime heat in Indian cities

{{COURSE}}, {{YEAR}}
Team: {{TEAM}}
Section: {{SECTION}}
Preliminary assessment: 6 November 2026

## Research topic

To what extent has the frequency of extreme nighttime heat changed relative
to extreme daytime heat across major Indian cities between 2001 and 2024?

The project uses daily maximum (Tmax) and minimum (Tmin) temperatures for
16 Indian cities to compare daytime and nighttime heat exposure. This can
inform the timing and location of heat-protection measures, including cooling
access and heat-response services.

## Data preparation

The source is IMD's one-degree gridded temperature data, covering 1 January
2001 to 31 December 2024. Temperatures are in degrees Celsius. The prepared
table has 140,256 city-day rows and
16 columns: city/date identifiers, temperatures, coordinates and missing flags.
Guwahati is missing one date, 26 June 2005, in both source files. That row is
retained with blank temperatures and missing flags.

The script checks dates, duplicates, coordinates and temperature consistency,
then joins Tmax and Tmin by location and date. It preserves source temperatures
and writes the complete city-date table to data/processed/daily_temperatures.csv.

## Reproduction

Python 3.11+ is required; the code was tested with Python 3.12.10.
From the assessment folder, run these commands in order:

    python -m pip install -r requirements.txt
    python src/prepare_data.py --skip-heat

Only this preparation script is needed for the preliminary dataset.
It also writes a city-year coverage table and validation summaries in JSON
and TXT format. The preparation settings are in config/preparation.json;
city names and coordinates are in config/cities.geojson.
