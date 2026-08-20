# Canonical Source and Mirror Sync

Edit the canonical `ferminfm/latex` subtree. Generate the standalone repository
with `scripts/export_standalone.py`; do not copy files by hand or merge mirror
changes back. The export metadata records source commit, file hashes, origins,
exclusions, and a tree digest. A future standalone release remains private until
the explicit exclusion, secret, portability, clean-clone, URL, and reuse-status
gates pass.
