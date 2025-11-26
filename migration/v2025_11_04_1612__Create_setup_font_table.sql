
CREATE TABLE IF NOT EXISTS setup_font (
    font_id         VARCHAR PRIMARY KEY,
    font_size       INTEGER,
    font_family     VARCHAR,
    font_weight     INTEGER DEFAULT 400
);
