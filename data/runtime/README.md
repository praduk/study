# Runtime data

Study stores revocable login sessions in `sessions.sqlite3`. That database and
its journal files are deliberately excluded from Git because they contain live
authentication tokens. Authored content and review history elsewhere under
`data/` are tracked.

