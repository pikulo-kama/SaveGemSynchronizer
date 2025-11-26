
CREATE TABLE IF NOT EXISTS app_state (
    user_id         VARCHAR PRIMARY KEY,
    language        VARCHAR,
    current_game    VARCHAR,
    time_format_id  INTEGER,
    color_theme     VARCHAR
);
