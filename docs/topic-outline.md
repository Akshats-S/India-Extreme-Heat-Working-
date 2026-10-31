# Extreme daytime and nighttime heat across 16 Indian cities, 2001-2024

**Research question:** To what extent has the frequency of extreme nighttime
heat changed relative to extreme daytime heat across major Indian cities
between 2001 and 2024?

This Environmental Economics project prepares a reproducible daily dataset
from India Meteorological Department (IMD) one-degree gridded maximum and
minimum temperatures accessed through https://imdweb.lwcc.in/ . The selected
points represent Delhi, Jaipur, Ahmedabad, Mumbai, Pune, Lucknow, Patna,
Kolkata, Bhopal, Nagpur, Hyderabad, Bengaluru, Chennai, Bhubaneswar, Guwahati
and Kochi from 1 January 2001 to 31 December 2024.

The preliminary output contains 140,256 expected city-day records, of which
140,255 have both temperatures. The sole absent observation is Guwahati on
26 June 2005, in both source files. The pipeline validates input structure,
dates, duplicates, coordinates and temperature consistency, joins Tmax/Tmin
by point/date, and retains the missing city-day with explicit flags. No
temperature values are imputed, rounded, deleted or converted. The package
includes the original inputs, preparation code and run instructions.

The environmental economics relevance is the allocation of adaptation
resources across locations and times of day. Exposure patterns can inform
questions about overnight cooling access, energy-efficient adaptation and
heat-response targeting. Evaluating costs, benefits or policy effectiveness
would also need population, cost and outcome data; the temperature dataset
does not itself establish those effects.

The full project uses fixed, city-specific calendar-day 90th-percentile
thresholds with five-day seasonal windows over 2001-2024. It compares annual
frequencies and 2001-2005 versus 2020-2024 percentages using observed dates.
The preliminary submission can be evaluated independently of these later
heat-indicator and descriptive-analysis outputs.

IMD documentation establishes Celsius. These are interpolated grid estimates,
not city weather-station readings or measurements of urban heat islands.
Exact export clock-time alignment remains unverified, so source dates are
retained and Tmin is a nighttime proxy. IMD also documents a station-network
change from 2008 onward. The project-relative indicators are not official
IMD heatwave classifications. Final output is a documented dataset and
replication package, with 2-3 economics research applications.
