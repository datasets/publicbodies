## Update Script Maintenance Report

Date: 2026-03-04

- Root cause: scheduled updater job was gated to `okfn/publicbodies`, so it never executed in `datasets/publicbodies`.
- Fixes made: corrected repository condition, added manual trigger, upgraded checkout/setup actions, and added `permissions: contents: write`.
- Validation: verified workflow condition and matrix update path for `br` and `it` sources.
- Known blockers: none identified in this remediation pass.
