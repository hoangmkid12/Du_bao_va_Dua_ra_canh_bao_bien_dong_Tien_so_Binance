from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os

spark = SparkSession.builder \
    .appName("CryptoRealTimeAnalytics") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.jars.excludes",
            "org.apache.hadoop:hadoop-client-runtime,"
            "org.apache.hadoop:hadoop-client-api") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("symbol", StringType()),
    StructField("price", DoubleType()),
    StructField("quantity", DoubleType()),
    StructField("is_buyer_maker", BooleanType()),
    StructField("timestamp", LongType())
])

print("Initializing Spark Streaming to Kafka...")

KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "crypto_trades"

df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", KAFKA_BROKER) \
  .option("subscribe", KAFKA_TOPIC) \
  .option("startingOffsets", "latest") \
  .load()

parsed_df = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")
parsed_df = parsed_df.withColumn("timestamp", (col("timestamp") / 1000).cast("timestamp"))

windowed_df = parsed_df \
    .withWatermark("timestamp", "5 seconds") \
    .groupBy(
        window(col("timestamp"), "5 seconds"),
        col("symbol")
    ) \
    .agg(
        avg("price").alias("avg_price"),
        sum("quantity").alias("total_volume"),
        sum(when(col("is_buyer_maker") == False, col("quantity")).otherwise(0)).alias("buy_volume"),
        sum(when(col("is_buyer_maker") == True, col("quantity")).otherwise(0)).alias("sell_volume"),
        max("price").alias("high"),
        min("price").alias("low"),
        first("price").alias("open"),
        last("price").alias("close")
    )

output_df = windowed_df.select(
    col("window.start").alias("window_start"),
    col("window.end").alias("window_end"),
    "symbol", "avg_price", "total_volume", "buy_volume", "sell_volume", "high", "low", "open", "close"
)

def write_to_csv(batch_df, batch_id):
    if not batch_df.isEmpty():
        file_path = "/app/data/realtime_crypto.csv"
        pdf = batch_df.toPandas()
        
        # Chỉ giữ lại 100 dòng mới nhất để tránh nghẽn I/O
        if os.path.exists(file_path):
            try:
                # Đọc nhanh 100 dòng cuối thay vì toàn bộ
                existing_pdf = __import__('pandas').read_csv(file_path).tail(100)
                combined_pdf = __import__('pandas').concat([existing_pdf, pdf])
                combined_pdf = combined_pdf.drop_duplicates(subset=['window_start', 'symbol'], keep='last').tail(100)
                combined_pdf.to_csv(file_path, index=False)
            except:
                pdf.to_csv(file_path, index=False)
        else:
            pdf.to_csv(file_path, index=False)

query = output_df \
    .writeStream \
    .outputMode("update") \
    .foreachBatch(write_to_csv) \
    .trigger(processingTime='1 second') \
    .start()

print("Spark Streaming started! Waiting for data...")
query.awaitTermination()
