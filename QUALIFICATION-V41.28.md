# OpenVisio v41.28 — Phase timing instrumentation

Author: Abdelhalim Talbi

The existing renderer now measures mutation reconciliation, cable diagnostics, routing pipeline, edge DOM, node DOM, and cleanup using performance.now(). Results are accessible via lastRenderPhaseProfile(svg). Timing is observational, no new cache or routing engine. The routing pipeline phase aggregates route calculation, obstacle handling and fanout; subphase attribution is not yet available. Browser layout/paint and Windows are NOT measured.
