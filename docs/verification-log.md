# Verification log

The handout asks every group member to verify each step of the code, because AI tools can make mistakes. Record each check here. A step is only "verified" once a **person** has read the code and checked its output; an assistant's own check does not count as human verification.

| Step / script | What was checked | How | Verified by | Date |
|---|---|---|---|---|
| `src/audit_raw_data.py` | Output matches an independent pandas check (row counts 140,255 per file, 16 points, no empty cells, no duplicate keys, one missing location-date: point 14 on 2005-06-26, files match on keys) | AI assistant ran both and compared | _human verification pending_ | |
| `config/cities.geojson` | 16 city points match the point coordinates in both CSVs, in point_id order | AI assistant compared programmatically | _human verification pending_ | |
