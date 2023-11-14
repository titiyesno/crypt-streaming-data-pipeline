import sched
import time
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import collect_list, struct, col, expr, sum, lit


KAFKA_BOOTSTRAP_SERVER="kafka:29092"
KAFKA_TOPIC="order_book_sum"

TIMESCALE_DBNAME="technical_assessment"
TIMESCALE_HOST=f"jdbc:postgresql://timescale:5432/{TIMESCALE_DBNAME}"
TIMESCALE_TABLE="order_book_sum"
TIMESCALE_USER="postgres"
TIMESCALE_PASSWORD="password"


def main():
    spark = SparkSession.builder \
            .appName("Spark-Publish") \
            .master("spark://spark:7077") \
            .config("spark.executor.memory", "1536m") \
            .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")  
    
    df = spark.read \
        .format("jdbc") \
        .option("driver", "org.postgresql.Driver") \
        .option("url", TIMESCALE_HOST) \
        .option("dbtable", TIMESCALE_TABLE) \
        .option("user", TIMESCALE_USER) \
        .option("password", TIMESCALE_PASSWORD) \
        .load()
    
    df.cache()
    
    # Aggregate the rows into a single column and convert to JSON array
    json_array_df = df.selectExpr("to_json(collect_list(struct(*))) as value")

    # Write the JSON array to Kafka
    json_array_df.selectExpr("CAST('key' AS STRING) AS key", "value") \
        .write \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVER) \
        .option("topic", KAFKA_TOPIC) \
        .save()
    
    print("sent to kafka")
    df.unpersist()    
    scheduler.enter(1, 1, main, ())


if __name__ == "__main__":
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(1, 1, main, ())
    scheduler.run()