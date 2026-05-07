import json
import time
import websocket
from kafka import KafkaProducer

KAFKA_BROKER = 'kafka:9092'
TOPIC_NAME = 'crypto_trades'

print(f"Connecting to Kafka at {KAFKA_BROKER}...")
print(f"Connecting to Kafka at {KAFKA_BROKER}...")
producer = None
while producer is None:
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("Connected to Kafka successfully!")
    except Exception as e:
        print(f"Kafka Connection Error: {e}. Retrying in 5 seconds...")
        time.sleep(5)

def on_message(ws, message):
    payload = json.loads(message)
    # Với combined stream, dữ liệu trade nằm trong payload['data']
    data = payload.get('data')
    if not data: return
    
    trade = {
        'symbol': data['s'],
        'price': float(data['p']),
        'quantity': float(data['q']),
        'is_buyer_maker': bool(data['m']), # True = Lệnh Bán chủ động (Sell), False = Lệnh Mua chủ động (Buy)
        'timestamp': data['E']
    }
    producer.send(TOPIC_NAME, trade)
    action = "SELL" if trade['is_buyer_maker'] else "BUY"
    print(f"{action} -> {trade['symbol']} | Price: ${trade['price']:.2f} | Qty: {trade['quantity']:.4f}")

def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed.")

def on_open(ws):
    print("WebSocket opened successfully! Listening to Multiple trades...")

if __name__ == "__main__":
    websocket.enableTrace(False)
    # Combined Stream: Lắng nghe 5 đồng coin lớn nhất
    streams = "btcusdt@trade/ethusdt@trade/bnbusdt@trade/solusdt@trade/xrpusdt@trade"
    socket_url = f"wss://stream.binance.com:9443/stream?streams={streams}"
    
    ws = websocket.WebSocketApp(socket_url,
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close)
    
    while True:
        ws.run_forever()
        print("Reconnecting in 5 seconds...")
        time.sleep(5)
