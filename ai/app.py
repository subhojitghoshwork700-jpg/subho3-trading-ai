import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

# পেজ সেটআপ
st.set_page_config(page_title="XAU/USD Live AI Tracker", layout="wide", page_icon="🟡")

st.title("🟡 XAU/USD (Spot Gold) Real-Time AI Analyzer")

# ডাটা সংগ্রহের ফাংশন - ১ মিনিটের টাইমফ্রেম ব্যবহার করা হয়েছে একদম কারেন্ট ডাটার জন্য
@st.cache_data(ttl=5) # প্রতি ৫ সেকেন্ডে ডাটা রিফ্রেশ হবে
def get_live_gold_data():
    try:
        # Yahoo Finance এ 'GC=F' ফিউচারস হলেও এটি স্পট প্রাইসের সবচেয়ে কাছাকাছি থাকে
        # ১ মিনিটের ইন্টারভ্যাল ব্যবহার করা হয়েছে যাতে কোনো লেট না হয়
        df = yf.download(tickers='GC=F', period='1d', interval='1m', progress=False)
        
        # ডাটা ক্লিনিং (মাল্টি-ইনডেক্স সমস্যা দূর করা)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        return df
    except Exception as e:
        return None

df = get_live_gold_data()

if df is not None and not df.empty:
    # সর্বশেষ প্রাইস এবং সময়
    last_price = round(float(df['Close'].iloc[-1]), 2)
    last_time = df.index[-1].strftime('%H:%M:%S')

    # ড্যাশবোর্ড ডিসপ্লে
    st.metric(label="Live Spot Gold Price", value=f"${last_price}", delta=f"Updated at {last_time}")

    # ইন্ডিকেটর ক্যালকুলেশন
    df['RSI'] = ta.rsi(df['Close'], length=14)
    df['EMA_10'] = ta.ema(df['Close'], length=10) # আরও ফাস্ট ট্রেন্ড বোঝার জন্য EMA 10
    
    current_rsi = round(float(df['RSI'].iloc[-1]), 2)

    # এআই সিগন্যাল (হাই স্পিড লজিক)
    st.subheader("🤖 Real-Time AI Signal")
    if current_rsi < 30:
        st.success("🚀 **BUY NOW!** মার্কেট অনেক নিচে (Oversold), এখন উপরে যাওয়ার সময়।")
    elif current_rsi > 70:
        st.error("📉 **SELL NOW!** মার্কেট অনেক উপরে (Overbought), এখন নিচে নামার সম্ভাবনা।")
    else:
        st.info("⚖️ **WAIT.** মার্কেট এখন ব্যালেন্সড অবস্থায় আছে।")

    # ক্যান্ডেলস্টিক চার্ট
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'], name='Price')])
    
    fig.update_layout(template='plotly_dark', height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("লাইভ ডাটা কানেক্ট করতে সমস্যা হচ্ছে। দয়া করে পেজটি রিফ্রেশ দিন।")

st.caption("টিপস: একদম প্রপার ১ সেকেন্ডের লাইভ ডাটা পেতে ব্রাউজারে রিফ্রেশ দিন।")