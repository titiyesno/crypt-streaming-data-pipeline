CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS raw_order_book(
    order_id INTEGER,
    symbol VARCHAR(10),
    order_side VARCHAR(10),
    size DOUBLE PRECISION,
    price DOUBLE PRECISION,
    status VARCHAR(10),
    created_at BIGINT NOT NULL,
    event_timestamp TIMESTAMPTZ
);

CREATE INDEX idx_order_status ON raw_order_book(status, order_id);

SELECT create_hypertable('raw_order_book', 'event_timestamp', chunk_time_interval => INTERVAL '1 second');

CREATE VIEW order_book_sum 
AS
WITH raw_order AS (
	SELECT 
		order_id,
		symbol,
		order_side,
		size,
		price
	FROM raw_order_book robo  
	WHERE NOT EXISTS (
		SELECT 1 FROM raw_order_book robc 
		WHERE robo.order_id = robc.order_id 
		AND STATUS = 'CLOSED'
	)
) 
SELECT 
	symbol,
	CONCAT(order_side, '_', order_id) AS side,
	price,
	size AS amount,
	price * size AS total,
	sum(price * size) OVER (PARTITION BY order_side ORDER BY order_id) AS cum_sum 
FROM raw_order
ORDER BY order_id;

