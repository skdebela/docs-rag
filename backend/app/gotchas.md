# gotchas.md

## Centralized Error Handling
- If you see `'generator' object has no attribute 'execute'` in `/api/health`, it means the DB health check was using the dependency generator incorrectly. Fix: use `session_gen = get_db(); session = next(session_gen); session.execute(text("SELECT 1"))`.
- If you see `Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')`, you must wrap raw SQL in `text()` with SQLAlchemy 2.x+.

## Vectorstore
- Chroma delete API may not fully clear in-memory cache; after delete, always re-initialize vectorstore.

## Admin Token
- Admin token must be 8–128 characters, only alphanumeric, dash, or underscore. Invalid tokens return 422.

## Validation
- File upload: Only extensions in SUPPORTED_EXTENSIONS are allowed. Others return 422.
- Chat: Question must be 3–500 chars or returns 422.

## Logging
- All errors and operational events should be logged with `safe_log_gotcha` for compliance and debugging.

---

_Last updated: 2025-04-29 22:16:48+02:00_
