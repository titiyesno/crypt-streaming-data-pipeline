# crypt-streaming-data-pipeline

Below are the step to run the streaming data pipeline and check the output:
- Execute `docker compose up`
- Open kafka at localhost:9000. The results are in `order_book_sum` topic
- Open grafana at localhost:3000 and go to the `Order book` dashboard. Set auto-refresh to 5s and wait for it to refresh.
