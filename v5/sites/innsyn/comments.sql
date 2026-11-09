-- Additive migration in the existing EU D1 database. No raw IPs or email addresses.
CREATE TABLE IF NOT EXISTS comments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  article TEXT NOT NULL,
  name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 80),
  body TEXT NOT NULL CHECK(length(body) BETWEEN 1 AND 6000),
  parent_id INTEGER REFERENCES comments(id) ON DELETE SET NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','published')),
  created_at INTEGER NOT NULL,
  published_at INTEGER,
  nonce TEXT NOT NULL UNIQUE,
  reports INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS comments_public ON comments(article,status,id);
CREATE INDEX IF NOT EXISTS comments_queue ON comments(status,created_at);
CREATE INDEX IF NOT EXISTS comments_parent ON comments(parent_id);
CREATE TABLE IF NOT EXISTS comment_limits (
  key TEXT PRIMARY KEY,
  count INTEGER NOT NULL,
  permit TEXT NOT NULL,
  expires_at INTEGER NOT NULL
) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS comment_limits_expiry ON comment_limits(expires_at);
CREATE TABLE IF NOT EXISTS comment_reports (
  comment_id INTEGER NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
  reporter TEXT NOT NULL,
  expires_at INTEGER NOT NULL,
  PRIMARY KEY(comment_id,reporter)
) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS comment_reports_expiry ON comment_reports(expires_at);
CREATE TABLE IF NOT EXISTS comment_actions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  comment_id INTEGER NOT NULL,
  action TEXT NOT NULL CHECK(action IN ('publish','delete','dismiss_reports')),
  created_at INTEGER NOT NULL
);
