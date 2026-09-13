# Dense-routing measurements

`benchmark_dense_routing.py` is a deterministic, geometry-only stress fixture:
64 staggered tank bodies (alternating rotations) with 16 opposing horizontal and
vertical routes across the entire field. It exercises obstacle detours rather
than the adjacent links in `benchmark_routing.py`. Ports are synthetic external
endpoints; this fixture does not measure a complete document or canvas rendering.

Run from the project folder with `.venv\Scripts\python.exe benchmark_dense_routing.py`.
The fixture size is bounded to 2–12 rows/columns; default is 8. `run(size=..., refreshes=...)`
is available for other bounded sizes. Results report failures and validate every
successful route's endpoints, orthogonality and clearance against all obstacles.
Pipe crossings and collinear pipe overlaps are permitted by the current router;
this does not test line separation, automatic bridges, or engineering correctness.

## Baseline on this development machine

Measured September 11, 2026, Python 3.14.2:

| Case | Seconds |
| --- | ---: |
| Initial route calculation, 16 pipes | 1.0190 |
| Unchanged cached refresh, average of 10 | 0.0000455 |
| One obstacle moved 5 units in each axis | 0.9874 |

Both original and moved cases returned zero route failures and zero invalid
successful routes. The cached phase recorded 160 hits. These are observations,
not timing guarantees or unit-test thresholds.

The large difference matters: every route cache key contains **all** obstacle
boxes. Moving any equipment invalidates each key, so fast unchanged refreshes do
not establish smooth dragging. The approximately one-second geometry calculation
is a remaining responsiveness concern for this synthetic layout.

A separate `cProfile` run (whose overhead is excluded from the table) attributed
3.791 seconds cumulatively to 32 `segment` searches across initial and moved
layouts. Of that, 1.354 seconds was spent in 266,499 `clear` calls; search bookkeeping
also contributed substantially. This suggests shared obstacle/visibility indexing
and reduced repeated search work as investigation targets. Merely enlarging the
full-route cache will not help continuous geometry changes.

`test_dense_routing.py` uses a small 4×4 version for fast deterministic regression
checks: no failures, correct clear paths, identical cached paths, cache hits and
clear paths after an obstacle move. It deliberately has no environment-sensitive
wall-time assertion. The dense fixture plus existing routing/geometry tests passed
9 tests in 0.071 seconds. The default 8×8 benchmark was also executed and checked.

## After interval-index optimization

The router now indexes merged obstacle-interior intervals for each visibility
grid line, querying them with binary search instead of scanning every box for
each edge. A subsequent normal run measured:

| Case | Seconds |
| --- | ---: |
| Initial route calculation, 16 pipes | 0.4813 |
| Unchanged cached refresh, average of 10 | 0.0000435 |
| One obstacle moved 5 units in each axis | 0.4703 |

Both layouts still produced zero failures and zero invalid routes. This is about
2.1× faster than the recorded baseline for changed geometry, but approximately
half a second remains material for interactive dragging and is not a smooth-UI
claim. Further search/recalculation work is still warranted.

An independent comparison of 100 seeded layouts with overlapping boxes produced
exactly the same point sequences before and after optimization. Regression tests
also check those routes remain deterministic and clear. Indexed span queries
are compared against the original box-scan predicate for 2,662 horizontal and
vertical cases, including boundary touches, reversed endpoints, overlapping and
touching boxes, zero-width/height boxes and zero-length segments.
# Viewport drag follow-through

`benchmark_dense_drag.py` constructs a valid 96-component document: the same
64 staggered tanks plus 32 endpoint valves and 16 crossing pipes. It dispatches
actual Qt viewport press/move/release events and checks every route after each
move, endpoint attachment, and exact undo/redo restoration.

On September 11, 2026, disabling interactive reuse measured four move events at
0.614, 0.629, 0.586 and 0.588 seconds. With reuse enabled the same gesture measured
0.008, 0.008, 0.035 and 0.006 seconds. Release took 0.617 seconds with reuse versus
0.009 seconds without it (the old path had already done all work during movement).
These are local offscreen Qt event measurements, not a universal frame-rate claim.

Only unchanged-endpoint/direction/waypoint routes whose every segment remains
clear are reused while dragging. Obstructed or attached routes recalculate
immediately. Release always recomputes canonical routes; no route cache is saved
in the document. This preserves deterministic reopened geometry and avoids stale
endpoints. Release can still pause briefly in this dense case. Tests in
`test_dense_drag.py` cover real movement, history, collision invalidation,
endpoint invalidation, final refresh and saved/reopened route equality.
