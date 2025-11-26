
CREATE TABLE IF NOT EXISTS game_settings (
    user_id             VARCHAR,
    game_name           VARCHAR,
    auto_mode_enabled   INTEGER,

    PRIMARY KEY (user_id, game_name)
);
