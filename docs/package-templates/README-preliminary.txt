Data source: [India Meteorological Department, via IMDWeb](https://imdweb.lwcc.in/).

# Extreme daytime and nighttime heat in Indian cities

**Course:** {{COURSE}}, {{YEAR}}

**Team:** {{TEAM}}

Section: {{SECTION}}

**Preliminary assessment:** 6 November 2026

## Research topic

To what extent has the frequency of extreme nighttime heat changed relative
to extreme daytime heat across major Indian cities between 2001 and 2024?

The daily maximum temperature (Tmax) and minimum temperature (Tmin) are used
for this project, which covers 16 Indian cities. Comparing daytime and
nighttime heating can help identify suitable places and times to implement
heat mitigation measures.

## Data preparation

The source is the one-degree gridded temperature data provided by IMD,
covering 1 January 2001 to 31 December 2024. Temperatures are in degrees
Celsius. The prepared dataset contains 140,256 records and 16 variables,
including city, date, temperatures, coordinates and missing-data flags.
Guwahati is missing one date (26 June 2005) in both source datasets. This
record is kept with blank temperatures and flags indicating the missing data.

The script checks dates, duplicate records, coordinates and temperatures
before combining Tmax and Tmin by location and date. It preserves the
original temperature values and saves the complete city-date table as
`data/processed/daily_temperatures.csv`.

## Reproduction

Python 3.11+ is required; the code was tested with Python 3.12.10.
Open a terminal in the folder containing `Preliminary Assessment - Group 3`.
Run these commands in order. If you are already inside the assessment folder,
skip the first command.

    cd "Preliminary Assessment - Group 3"
    python -m pip install -r requirements.txt
    python src/prepare_data.py --skip-heat

Run this one script to create the cleaned preliminary dataset. It also saves
a summary of the available data for each city and year, plus the results of
its data checks in two files: one for software (JSON) and one you can read
(TXT). The script reads its settings from `config/preparation.json` and the
city names and locations from `config/cities.geojson`.
