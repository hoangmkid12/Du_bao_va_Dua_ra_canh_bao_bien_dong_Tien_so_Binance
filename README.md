# Dự báo và Đưa ra Cảnh báo Biến động Tiền số Binance
(Crypto Anomaly Detection)

Dự án này là một hệ thống phát hiện bất thường và theo dõi biến động tiền điện tử (đặc biệt là theo dõi "Cá voi" - Whale activity) theo thời gian thực. Hệ thống thu thập dữ liệu giao dịch từ Binance thông qua WebSocket, xử lý luồng dữ liệu lớn (Big Data) bằng **Apache Kafka** và **PySpark Structured Streaming**, sau đó trực quan hóa dữ liệu và đưa ra cảnh báo trên giao diện **Streamlit**.

## 🚀 Kiến trúc Hệ thống

Dự án sử dụng kiến trúc Big Data pipeline hiện đại:

1.  **Thu thập dữ liệu (Ingestion):** Sử dụng `websocket-client` kết nối tới API WebSocket của Binance để lấy dữ liệu giao dịch (Trade data) theo thời gian thực của các cặp tiền điện tử.
2.  **Message Broker:** Apache Kafka nhận và lưu trữ luồng dữ liệu tốc độ cao, đảm bảo tính bền vững (durability), không mất mát dữ liệu và tách biệt producer với consumer.
3.  **Xử lý luồng (Stream Processing):** PySpark Structured Streaming (chạy trên Spark Standalone cluster với Master và Worker) đọc dữ liệu từ Kafka. Nó tính toán các chỉ số (tổng khối lượng giao dịch, giá trung bình) theo các cửa sổ thời gian (time windows) và phát hiện các giao dịch bất thường (ví dụ: khối lượng giao dịch lớn đột biến).
4.  **Lưu trữ & Trực quan hóa (Storage & Visualization):** Dữ liệu sau khi xử lý qua Spark được lưu xuống định dạng CSV. Streamlit đọc dữ liệu này để hiển thị biểu đồ thời gian thực, bảng thống kê và cảnh báo.
5.  **Báo cáo (Reporting):** Hệ thống tích hợp tính năng xuất báo cáo tự động ra file Word (`.docx`) kèm theo biểu đồ và các nhận định phân tích.

## 🛠️ Công nghệ sử dụng

*   **Ngôn ngữ:** Python 3.x
*   **Big Data & Streaming:** Apache Kafka, Apache Zookeeper, Apache Spark (PySpark 3.5.1)
*   **Trực quan hóa (Frontend/Dashboard):** Streamlit, Plotly, Matplotlib
*   **Triển khai:** Docker & Docker Compose
*   **Thư viện khác:** `pandas`, `numpy`, `kafka-python`, `python-docx`

## 📂 Cấu trúc Thư mục

```text
Project_Crypto/
├── data/                   # Thư mục chứa dữ liệu CSV sau khi xử lý bằng Spark
├── report_assets/          # Chứa các tài nguyên (hình ảnh, biểu đồ) dùng cho báo cáo Word
├── src/                    # Chứa toàn bộ mã nguồn Python
│   ├── binance_producer.py # Script lấy dữ liệu từ Binance và đẩy vào Kafka
│   ├── spark_streaming.py  # Script xử lý dữ liệu luồng từ Kafka, tính toán và lưu ra CSV
│   └── dashboard.py        # Ứng dụng Streamlit hiển thị Dashboard (được gọi qua start.sh)
├── docker-compose.yml      # Cấu hình triển khai hệ thống (Kafka, Zookeeper, Spark, Streamlit)
├── Dockerfile.streamlit    # Dockerfile build image riêng cho Streamlit app
├── start.sh                # Script entrypoint khởi chạy toàn bộ luồng pipeline trong container Streamlit
├── requirements.txt        # Danh sách thư viện Python cần thiết
├── generate_report.py      # Script tự động tạo báo cáo Word
├── export_report.py        # Script phụ trợ xuất dữ liệu báo cáo
└── export_luong.py         # Script mô phỏng/báo cáo luồng hoạt động
```

## ⚙️ Hướng dẫn Cài đặt và Chạy hệ thống

Hệ thống được thiết kế chạy trên các container bằng Docker, giúp việc triển khai dễ dàng mà không cần setup môi trường phức tạp trên máy tính cá nhân.

### Yêu cầu tiên quyết:
*   Đã cài đặt **Docker Desktop** (hoặc Docker Engine & Docker Compose).

### Các bước khởi chạy:

1.  **Clone repository:**
    ```bash
    git clone https://github.com/hoangmkid12/Du_bao_va_Dua_ra_canh_bao_bien_dong_Tien_so_Binance.git
    cd Du_bao_va_Dua_ra_canh_bao_bien_dong_Tien_so_Binance
    ```

2.  **Khởi động các dịch vụ bằng Docker Compose:**
    Tại thư mục gốc của dự án, chạy lệnh:
    ```bash
    docker-compose up -d --build
    ```
    *Quá trình này sẽ tự động tải các image cần thiết (Zookeeper, Kafka, Spark Master/Worker) và build image riêng cho Streamlit. Container Streamlit sẽ tự động gọi file `start.sh` để kích hoạt Producer, Spark Streaming và Dashboard.*

3.  **Truy cập vào ứng dụng:**
    *   **Streamlit Dashboard:** Truy cập [http://localhost:8501](http://localhost:8501)
    *   **Spark Master UI:** Truy cập [http://localhost:8080](http://localhost:8080) (để theo dõi trạng thái cluster Spark)
    
    *(Lưu ý: Bạn có thể cần đợi từ 30 giây đến 1 phút để Kafka khởi động xong, kết nối WebSocket hoạt động và Spark bắt đầu xử lý micro-batches đầu tiên thì dữ liệu mới hiện lên Dashboard).*

### Tắt hệ thống:
Để dừng hệ thống và dọn dẹp các container:
```bash
docker-compose down
```

## 📝 Chức năng chính của Dashboard (Streamlit)
*   **Biểu đồ Real-time:** Đồ thị đường hiển thị giá trị tiền điện tử và biểu đồ khối lượng giao dịch cập nhật liên tục mỗi giây.
*   **Cảnh báo Cá voi (Whale Alerts):** Khu vực cảnh báo ngay lập tức hiển thị khi phát hiện các giao dịch mua/bán với khối lượng cực lớn vượt qua các ngưỡng động (dynamic threshold).
*   **Thống kê Thị trường (Market Metrics):** Cung cấp cái nhìn tổng quan thông qua các KPI như giá cao nhất/thấp nhất, độ biến động trong khoảng thời gian phân tích.
*   **Xuất Báo Cáo Word:** Cung cấp tính năng tự động tạo và tải xuống báo cáo phân tích học thuật bao gồm kiến trúc, phương pháp phát hiện bất thường và các biểu đồ bằng file `.docx`.

## 🤝 Tác giả: Nguyễn Hoàng Mỹ

Dự án nhằm mục đích trình diễn khả năng xây dựng Data Pipeline cho bài toán Big Data theo thời gian thực (Real-time Streaming Analytics).

Repository: [Du_bao_va_Dua_ra_canh_bao_bien_dong_Tien_so_Binance](https://github.com/hoangmkid12/Du_bao_va_Dua_ra_canh_bao_bien_dong_Tien_so_Binance)
