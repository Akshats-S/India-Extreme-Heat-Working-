# Source metadata and measurement limits

Checked 2026-10-31. Machine-readable evidence and source links are recorded in
`config/source_metadata.json`; the pipeline fingerprints that file in its report.

## Verified product properties

IMD's [maximum-temperature product page](https://www.imdpune.gov.in/cmpg/Griddata/Max_1_Bin.html)
specifies Celsius, leap-year coverage and a 31-by-31 grid. Its coordinate axes
run from latitude 7.5 to 37.5 N and longitude 67.5 to 97.5 E in one-degree steps.
The supplied control-file example uses 99.9 as the undefined-value sentinel.

The [minimum-temperature product page](https://www.imdpune.gov.in/cmpg/Griddata/Min_1_Bin.html)
gives matching units and grid structure. It also notes that 2008 onward uses
fewer stations (around 180). This network change can affect comparisons over
time and must be acknowledged in results.

IMD's cited [product paper](https://www.imdpune.gov.in/cmpg/Griddata/Research%20paper.pdf)
describes interpolation from quality-controlled station observations to a
one-degree grid. Cite: Srivastava, A. K., Rajeevan, M., and Kshirsagar, S. R.
(2009), *Development of a high resolution daily gridded temperature data set
(1969-2005) for the Indian region*, Atmospheric Science Letters,
[doi:10.1002/asl.232](https://doi.org/10.1002/asl.232).

The older paper describes the original product, not independent validation of
every later extension. The current product pages supply the later coverage.

## Export interpretation and spatial checks

The CSV headers do not themselves encode units or prove that the download
interface left the numerical scale unchanged. Celsius is assigned from the
documented IMD product identified in the project's provenance; no conversion
is made. This is a source-provenance interpretation, rather than a claim to
have compared every CSV value with a separately downloaded binary archive.

The retained `*_cell_lat` and `*_cell_lon` fields match nearest nodes on IMD's
documented grid for all 16 city points in both variables. This is checked
programmatically, allowing either node in an exact distance tie. The check
establishes agreement with nearest-grid sampling; it does not establish the
interface's undocumented implementation or turn a grid value into an urban
station observation. Coastal/topographic and urban-scale representation remain
limitations. These are interpolated grid estimates, not proven averages over
a city boundary or a formally defined one-degree polygon.

## Dates and nighttime interpretation

The product pages and original paper identify daily maxima/minima, but do not
establish the exact clock-time window and date-label convention of these CSVs.
Station-forecast API observation times cannot establish the convention of a
different historical gridded product. Accordingly:

- Keep each source date unchanged; do not shift Tmin backward or forward.
- Use Tmax/Tmin as daytime/nighttime proxies, respectively.
- Interpret a compound flag as two exceedances on the same **source date**;
  do not assert that it identifies a chronologically consecutive day and night.
- Do not calculate overnight duration or hourly heat exposure from these data.

This explicit measurement policy resolves how the pipeline handles dates; the
exact clock-time alignment remains an evidence limitation, not a fabricated
verified fact.

## Quality-control choices

`config/preparation.json` now sets broad project screening limits of -90 to
60 degrees Celsius, inclusive. These are deliberately loose safety bounds for
detecting sentinels/unit or parsing errors. They are not official IMD heatwave
criteria or proof that every value inside them is locally plausible. Out-of-range
records cause a reported validation failure; they are never clipped or deleted.
The final source-contract check also rejects IMD's documented 99.9 sentinel,
even if a custom preparation configuration relaxes the broad upper bound.

Finite values, unique keys, full calendar coverage, nearest-grid agreement,
cross-file grid agreement and Tmin <= Tmax are checked separately. The real
inputs pass these checks. Original CSVs and their full numerical precision
remain unchanged. The technical lead has already confirmed project data
sharing is resolved; no new general license is asserted here.
