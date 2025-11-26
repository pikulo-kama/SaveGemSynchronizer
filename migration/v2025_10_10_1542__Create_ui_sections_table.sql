
CREATE TABLE IF NOT EXISTS ui_sections (
    section_id      VARCHAR PRIMARY KEY,
    section_label   VARCHAR NOT NULL,
    section_icon    VARCHAR,
    controller      VARCHAR,
    order_id        INTEGER NOT NULL
);
