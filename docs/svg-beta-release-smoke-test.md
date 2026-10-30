# Aria piano SVG icon parity

This development-only smoke-test commit triggers the normal Validate -> beta publish pipeline after the canonical shared A/logo SVG change.

Check the published stable and beta site from the same source-of-truth SVG at `icons/aria.svg`. Android launcher PNGs in both channels must be byte-identical in each size, while app names remain separate (`Aria piano` and `Aria piano (beta)`).

The service worker cache version changes to v2 so old installed icons are refreshed. This note stays out of main unless explicitly approved, preserving the beta-first review policy.
