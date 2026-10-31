# Extreme daytime and nighttime heat in Indian cities

To what extent has the frequency of extreme nighttime heat changed relative
to extreme daytime heat across major Indian cities between 2001 and 2024?

The project uses daily maximum (Tmax) and minimum (Tmin) temperatures from
[India Meteorological Department, via IMDWeb](https://imdweb.lwcc.in/).
It covers 16 city-associated grid points from 1 January 2001 to 31 December
2024. The source has one-degree spatial resolution. Tmax and Tmin provide
proxies for daytime and nighttime heat exposure.

Comparing the two exposure patterns can inform the timing and location of
adaptation measures, including cooling access, heat-response services and
energy-efficient protection. The dataset supports research on how adaptation
resources are allocated across cities and times of day.

Preparation joins the two temperature files by location and date, checks their
consistency and preserves missing observations. The complete table has 140,256
city-day rows; Guwahati, 26 June 2005 is absent in both source files and remains
blank and flagged.
