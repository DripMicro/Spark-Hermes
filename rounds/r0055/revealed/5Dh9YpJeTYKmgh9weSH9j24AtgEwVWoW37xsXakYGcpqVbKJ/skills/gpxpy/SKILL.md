---
name: gpxpy
description: Layout and known weak spots of the gpxpy checkout (GPX track file parsing and geographic calculations). Load when the issue imports gpxpy.
---
# gpxpy checkout

- Package at `/testbed/gpxpy/`: `gpx.py` (track, segment, point, route, waypoint classes and their
  statistics), `geo.py` (distance, elevation, location math), `gpxfield.py` (XML field conversion and time
  parsing), `parser.py`, `utils.py`. Sample files in `/testbed/test_files/`.
- The project's single test module sits at the repository root and is usually removed along with the
  hidden tests, so there may be no test suite to run. Your check script is the only verification: make it
  cover the issue's example plus one neighbouring case (an empty segment, a single point, a point without
  elevation or time) so a careless edit does not break those.
- Weak spots: loops over points that stop after the first item or skip the last, accumulators that are
  reset inside the loop, `None` checks on optional elevation and time, units (metres against kilometres,
  degrees against radians), min/max swapped in bounds, and methods that should return a value but now
  return `None`.
- Many statistics methods have a sibling at another level (point, segment, track, whole file) computed the
  same way; compare with the sibling.
