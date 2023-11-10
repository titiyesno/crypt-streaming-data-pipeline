CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS raw_order_book(
    order_id INTEGER,
    symbol VARCHAR(10),
    order_side VARCHAR(10),
    size DOUBLE PRECISION,
    price DOUBLE PRECISION,
    status VARCHAR(10),
    created_at BIGINT NOT NULL
);

SELECT create_hypertable('raw_order_book', 'created_at', chunk_time_interval => 100000);
