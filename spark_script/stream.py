from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, StructField, LongType, DoubleType, IntegerType


KAFKA_BOOTSTRAP_SERVER="kafka:29092"
KAFKA_TOPIC="technical_assessment"
KAFKA_STARTING_OFFSET="earliest"

TIMESCALE_DBNAME="technical_assessment"
TIMESCALE_HOST=f"jdbc:postgresql://timescale:5432/{TIMESCALE_DBNAME}"
TIMESCALE_TABLE="raw_order_book"
TIMESCALE_USER="postgres"
TIMESCALE_PASSWORD="password"


def foreach_batch_function(df, epoch_id):
    df.write.format("jdbc")\
    .mode("append") \
    .option("driver", "org.postgresql.Driver") \
    .option("url", TIMESCALE_HOST)\
    .option("dbtable",TIMESCALE_TABLE)\
    .option("user",TIMESCALE_USER)\
    .option("password", TIMESCALE_PASSWORD)\
    .save()


def main():
    spark = SparkSession.builder \
            .appName("Spark-Streamingasd") \
            .master("spark://spark:7077") \
            .getOrCreate()
     
    spark.sparkContext.setLogLevel("ERROR")

    schema = StructType([ 
        StructField("order_id", IntegerType(), True),
        StructField("symbol" , StringType(), True),
        StructField("order_side" , StringType(), True),
        StructField("size" , DoubleType(), True),
        StructField("price" , DoubleType(), True),
        StructField("status" , StringType(), True),
        StructField("created_at" , LongType(), True)
        ])
    
    streaming_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", KAFKA_STARTING_OFFSET) \
    .load() \
    .select(
        from_json(col("value").cast("string"), schema).alias("parsed_value")
    ).select(col("parsed_value.*"))

    streaming_df.writeStream \
    .foreachBatch(foreach_batch_function)\
    .trigger(processingTime='1 seconds') \
    .start().awaitTermination()

    
if __name__ == "__main__":
    main()