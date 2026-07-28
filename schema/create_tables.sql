PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    influencer_name TEXT NOT NULL,
    budget REAL NOT NULL CHECK (budget > 0),
    expense_type TEXT NOT NULL,
    post_date DATE,
    payment_round TEXT,
    payment_status TEXT
);