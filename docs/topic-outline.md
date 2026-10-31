# Extreme daytime and nighttime heat across 16 Indian cities, 2001-2024

**Research question:** To what extent has the frequency of extreme nighttime
heat changed relative to extreme daytime heat across major Indian cities
between 2001 and 2024?

This project prepares a daily temperature dataset from India Meteorological
Department (IMD) one-degree gridded maximum (Tmax) and minimum (Tmin)
temperatures, accessed through https://imdweb.lwcc.in/ . It covers Delhi,
Jaipur, Ahmedabad, Mumbai, Pune, Lucknow, Patna, Kolkata, Bhopal, Nagpur,
Hyderabad, Bengaluru, Chennai, Bhubaneswar, Guwahati and Kochi, from
1 January 2001 to 31 December 2024.

The preliminary dataset joins both temperatures by city/date and preserves
source values and missingness. It has 140,256 expected city-day records,
including one absent pair: Guwahati, 26 June 2005. The preparation code checks
structure, dates, duplicates, coordinates and temperature consistency without
filling, rounding or deleting source temperatures.

The environmental economics motivation is the allocation of adaptation
resources across locations and times of day. Comparing daytime/nighttime
exposure can inform questions about overnight cooling access, energy-efficient
adaptation and heat-response targeting. Estimating costs, benefits or policy
effectiveness would require additional population, cost and outcome data.

These are interpolated grid estimates, not precise urban-station measurements.
Tmin is a nighttime proxy; source dates are retained because the export's
exact clock-time convention is unverified. Subsequent work compares unusually
warm days and nights; no heat-event or causal findings are claimed in this
preliminary outline.
