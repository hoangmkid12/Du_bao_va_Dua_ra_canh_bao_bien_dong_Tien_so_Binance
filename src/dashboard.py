import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import os
import numpy as np
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Hệ thống Theo dõi Cá mập Crypto",
    page_icon="🐋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS TỐI ƯU HIỂN THỊ & ĐỘ SÁNG ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0b0e14;
    }
    
    .stApp {
        background-color: #0b0e14;
    }
    
    /* Sidebar - Làm sáng văn bản và nền */
    [data-testid="stSidebar"] {
        background-color: #1a1d23 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }

    /* Các ô chỉ số cân đối */
    .metric-card {
        background: #1e2229;
        border-radius: 12px;
        border: 1px solid #30363d;
        padding: 20px;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    
    .metric-label {
        color: #9da5b1;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    
    .metric-value {
        color: #ffffff;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        font-weight: 800;
    }
    
    .block-container { padding-top: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# --- THANH SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color: #00d4ff; text-align: center; font-size: 2rem; margin-bottom: 0;'>🐋 WHALE PRO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #00d4ff; font-size: 0.7rem; margin-top: 0;'>BIG DATA ANALYTICS</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    selected_coin = st.selectbox("Chọn đồng Coin theo dõi:", ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT'])
    whale_multiplier = st.slider("Độ nhạy phát hiện:", 1.0, 5.0, 2.0)
    
    st.markdown("---")
    filepath = "data/realtime_crypto.csv" # Sử dụng file mới
    if os.path.exists(filepath):
        mtime = os.path.getmtime(filepath)
        if (time.time() - mtime) < 20:
            st.markdown("<div style='background: rgba(0, 255, 157, 0.1); border: 1px solid #00ff9d; padding: 10px; border-radius: 8px; color: #00ff9d; text-align: center; font-weight: bold;'>● Hệ thống: LIVE</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background: rgba(255, 171, 0, 0.1); border: 1px solid #ffab00; padding: 10px; border-radius: 8px; color: #ffab00; text-align: center; font-weight: bold;'>● Hệ thống: LAG</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='background: rgba(255, 73, 118, 0.1); border: 1px solid #ff4976; padding: 10px; border-radius: 8px; color: #ff4976; text-align: center; font-weight: bold;'>● Hệ thống: OFF</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

# --- GIAO DIỆN CHÍNH ---
st.markdown(f"<h2 style='color: white;'>Thị trường: <span style='color:#00d4ff'>{selected_coin}</span></h2>", unsafe_allow_html=True)

@st.fragment(run_every="1s")
def render_app(coin):
    # Dọn dẹp cache để đọc file mới nhất
    st.cache_data.clear()
    
    filepath = "data/realtime_crypto.csv" # Sử dụng file mới
    if not os.path.exists(filepath):
        st.info("Đang chờ dữ liệu...")
        return

    try:
        df = pd.read_csv(filepath)
        df['window_start'] = pd.to_datetime(df['window_start'])
        if df['window_start'].dt.tz is None:
            df['window_start'] = df['window_start'].dt.tz_localize('UTC')
        df['window_start'] = df['window_start'].dt.tz_convert('Asia/Ho_Chi_Minh').dt.tz_localize(None)
        
        df = df.sort_values('window_start').drop_duplicates(subset=['window_start', 'symbol'], keep='last')
        coin_df = df[df['symbol'] == coin].tail(45).copy()
        
        if coin_df.empty: return
        latest = coin_df.iloc[-1]
        
        # --- 4 Ô CHỈ SỐ CÂN ĐỐI ---
        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            is_up = latest['close'] >= latest['open'] if 'open' in latest else True
            color = "#00ff9d" if is_up else "#ff4976"
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Giá hiện tại</div>
                <div class='metric-value' style='color:{color}'>${latest['avg_price']:,.2f}</div>
                <div style='font-size:12px; color:{color}; font-weight:bold;'>{'▲ Tăng' if is_up else '▼ Giảm'}</div>
            </div>""", unsafe_allow_html=True)
            
        with m2:
            buy_p = (latest['buy_volume'] / latest['total_volume'] * 100) if latest['total_volume'] > 0 else 50
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Lực Mua chủ động</div>
                <div class='metric-value' style='color:#00d4ff'>{buy_p:.1f}%</div>
                <div style='background:#30363d; height:6px; border-radius:3px; margin-top:8px;'><div style='background:#00d4ff; width:{buy_p}%; height:6px; border-radius:3px;'></div></div>
            </div>""", unsafe_allow_html=True)
            
        with m3:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Biến động (5s)</div>
                <div class='metric-value'>${(latest['high'] - latest['low']):,.2f}</div>
                <div style='font-size:10px; color:#9da5b1;'>Biên độ: {latest['low']:,.1f}-{latest['high']:,.1f}</div>
            </div>""", unsafe_allow_html=True)
            
        with m4:
            delta = coin_df['avg_price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean().iloc[-1]
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
            rs = gain / (loss + 1e-9)
            rsi = 100 - (100 / (1 + rs)) if not np.isnan(rs) else 50
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Chỉ số RSI (14)</div>
                <div class='metric-value' style='color:#ffab00'>{rsi:.1f}</div>
                <div style='font-size:11px; color:#9da5b1;'>{'Trung tính' if 30<rsi<70 else ('Quá mua' if rsi>=70 else 'Quá bán')}</div>
            </div>""", unsafe_allow_html=True)

        # --- BIỂU ĐỒ ---
        st.write("")
        c1, c2 = st.columns([2.5, 1])
        
        with c1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=coin_df['window_start'], y=coin_df['avg_price'], 
                mode='lines', line=dict(color='#00d4ff', width=3)
            ))
            fig.update_layout(
                title=dict(text="BIẾN ĐỘNG GIÁ THỜI GIAN THỰC", font=dict(size=18, color='white')),
                template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                height=400, margin=dict(l=0, r=0, t=50, b=0),
                yaxis=dict(autorange=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)')
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
            
        with c2:
            fig_g = go.Figure(go.Indicator(mode="gauge+number", value=buy_p, title={'text': "CƯỜNG ĐỘ MUA (%)", 'font':{'size':14, 'color':'white'}}, gauge={'axis':{'range':[0,100]}, 'bar':{'color':"#00d4ff"}}))
            fig_g.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0)', font={'color':"white"})
            st.plotly_chart(fig_g, use_container_width=True, config={'displayModeBar': False})
            
            fig_v = go.Figure()
            fig_v.add_trace(go.Bar(x=coin_df['window_start'], y=coin_df['buy_volume'], marker_color='#00ff9d'))
            fig_v.add_trace(go.Bar(x=coin_df['window_start'], y=coin_df['sell_volume'], marker_color='#ff4976'))
            fig_v.update_layout(barmode='stack', height=120, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis=dict(visible=False), yaxis=dict(visible=False))
            st.plotly_chart(fig_v, use_container_width=True, config={'displayModeBar': False})

        # --- NHẬT KÝ ---
        st.markdown("### 📜 NHẬT KÝ GIAO DỊCH CÁ MẬP")
        mean_vol   = coin_df['total_volume'].mean()
        threshold  = mean_vol * whale_multiplier
        events = coin_df[coin_df['total_volume'] > threshold].tail(8).sort_values('window_start', ascending=False)

        # --- THANH THÔNG TIN NGƯỠNG ---
        st.markdown(f"""
        <div style='display:flex; gap:12px; margin-bottom:12px; flex-wrap:wrap;'>
            <div style='background:#1e2229; border:1px solid #30363d; border-radius:10px; padding:10px 18px; flex:1; min-width:160px;'>
                <div style='color:#9da5b1; font-size:0.72rem; font-weight:700; text-transform:uppercase; margin-bottom:4px;'>📊 Mean KL (45 phiên)</div>
                <div style='color:#ffffff; font-family:monospace; font-size:1.1rem; font-weight:800;'>{mean_vol:.4f} BTC</div>
            </div>
            <div style='background:#1e2229; border:1px solid #30363d; border-radius:10px; padding:10px 18px; flex:1; min-width:160px;'>
                <div style='color:#9da5b1; font-size:0.72rem; font-weight:700; text-transform:uppercase; margin-bottom:4px;'>⚙️ Hệ số nhạy</div>
                <div style='color:#ffab00; font-family:monospace; font-size:1.1rem; font-weight:800;'>{whale_multiplier:.1f}×</div>
            </div>
            <div style='background:rgba(0,212,255,0.08); border:1px solid #00d4ff; border-radius:10px; padding:10px 18px; flex:1; min-width:160px;'>
                <div style='color:#9da5b1; font-size:0.72rem; font-weight:700; text-transform:uppercase; margin-bottom:4px;'>⚡ Ngưỡng phát hiện</div>
                <div style='color:#00d4ff; font-family:monospace; font-size:1.1rem; font-weight:800;'>{threshold:.4f} BTC</div>
            </div>
            <div style='background:#1e2229; border:1px solid #30363d; border-radius:10px; padding:10px 18px; flex:1; min-width:160px;'>
                <div style='color:#9da5b1; font-size:0.72rem; font-weight:700; text-transform:uppercase; margin-bottom:4px;'>🐋 Số phiên cá mập</div>
                <div style='color:#{"00ff9d" if len(events)>0 else "ff4976"}; font-family:monospace; font-size:1.1rem; font-weight:800;'>{len(events)} / 45 phiên</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Format bảng nhật ký - đồng nhất với thông báo
        display_events = events[['window_start', 'buy_volume', 'sell_volume', 'avg_price', 'total_volume']].copy()
        display_events = display_events.rename(columns={
            'window_start': '🕒 Thời điểm',
            'buy_volume':   '🟢 KL Mua',
            'sell_volume':  '🔴 KL Bán',
            'avg_volume':   '📦 Tổng KL',
            'avg_price':    '💰 Giá TB ($)',
            'total_volume': '📦 Tổng KL'
        })
        display_events['💰 Giá TB ($)'] = display_events['💰 Giá TB ($)'].map('{:,.2f}'.format)
        display_events['🟢 KL Mua']     = display_events['🟢 KL Mua'].map('{:.4f}'.format)
        display_events['🔴 KL Bán']     = display_events['🔴 KL Bán'].map('{:.4f}'.format)
        display_events['📦 Tổng KL']    = display_events['📦 Tổng KL'].map('{:.4f}'.format)
        st.dataframe(display_events, use_container_width=True, hide_index=True)

        # --- THÔNG BÁO CÁ MẬP (chỉ bắn 1 lần cho mỗi phiên window mới) ---
        alert_key = f"last_whale_alert_{coin}"
        latest_window_str = str(latest['window_start'])
        if latest['total_volume'] > threshold:
            if st.session_state.get(alert_key) != latest_window_str:
                st.session_state[alert_key] = latest_window_str
                price_str  = f"{latest['avg_price']:,.2f}"
                vol_str    = f"{latest['total_volume']:.4f}"
                st.toast(
                    f"🚨 PHÁT HIỆN CÁ MẬP!\n"
                    f"Giá: ${price_str} | KL: {vol_str}",
                    icon="🐋"
                )

    except Exception as e:
        pass

render_app(selected_coin)
