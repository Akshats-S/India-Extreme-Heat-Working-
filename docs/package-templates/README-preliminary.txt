# Preliminary assessment: India extreme heat

{{COURSE}}, {{YEAR}}
Team: {{TEAM}}
Section: {{SECTION}}
6 November 2026

This folder contains the preliminary dataset, the code used to prepare it,
and the brief research-topic outline in TOPIC_OUTLINE.md.

## Dataset

`data/processed/daily_temperatures.csv` contains 140,256 city-day rows and
16 columns for 16 locations, 1 January 2001 to 31 December 2024. It includes
city, date, Tmax/Tmin, city/grid coordinates and missing-data flags. Both
original files omit Guwahati, 26 June 2005; that row remains blank and flagged.
No temperature is filled, rounded, clipped, deleted or converted.

Source: India Meteorological Department (IMD), via https://imdweb.lwcc.in/ .
Original inputs are included in data/raw/. Celsius and one-degree product
details: https://www.imdpune.gov.in/cmpg/Griddata/Max_1_Bin.html and
https://www.imdpune.gov.in/cmpg/Griddata/Min_1_Bin.html . Grid estimates are
not city weather-station measurements; Tmin is a nighttime proxy, with the
export's exact clock-time convention unverified.

## Run the preparation code

Use Python 3.11+ (tested with 3.12.10), open a terminal in this folder and run:

    python -m pip install -r requirements.txt
    python src/prepare_data.py --skip-heat

The code validates schemas, dates, unique point/date keys, coordinates,
numeric values and Tmin <= Tmax; constructs the full city-date calendar;
joins Tmax/Tmin; attaches city names; preserves missing observations; and
writes the sorted dataset. It also generates coverage and validation reports
as execution diagnostics. Those reports are not separate submission items.

The config files supply the city mapping and preparation settings. The brief
research topic, economics motivation and coverage are in TOPIC_OUTLINE.md.
