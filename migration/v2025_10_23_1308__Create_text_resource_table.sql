
CREATE TABLE IF NOT EXISTS setup_locale (
    locale_id   VARCHAR PRIMARY KEY,
    locale_name VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS setup_text_resource (
    text_resource_key   VARCHAR NOT NULL,
    locale_id           VARCHAR NOT NULL,
    text_resource       VARCHAR,

    PRIMARY KEY (text_resource_key, locale_id),
    FOREIGN KEY (locale_id) REFERENCES setup_locale(locale_id)
);
