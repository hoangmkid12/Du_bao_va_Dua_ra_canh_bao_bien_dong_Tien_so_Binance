#!/bin/bash

echo "Waiting for Kafka to be ready..."
while ! nc -z kafka 9092; do
  sleep 1
done
echo "Kafka is up!"

# Chạy Producer thu thập dữ liệu từ Binance
nohup python src/binance_producer.py > /tmp/producer.log 2>&1 &

# Chạy Spark Streaming xử lý dữ liệu và lưu xuống CSV
nohup python src/spark_streaming.py > /tmp/spark.log 2>&1 &

# Khởi chạy giao diện Streamlit Dashboard
streamlit run src/dashboard.py --server.port=8501 --server.address=0.0.0.0
