-- Aggregates only: no request log, IP address, cookie or visitor identifier.
CREATE TABLE IF NOT EXISTS daily_views (
  day TEXT NOT NULL,
  path TEXT NOT NULL,
  source TEXT NOT NULL,
  views INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (day, path, source)
) WITHOUT ROWID;
