import streamlit as st
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from tvdatafeed import TvDatafeed, Interval
from datetime import datetime

# পেজ সেটআপ
st.set_page_config(page_title="Gold AI Pro - TradingView", layout="wide", page_icon="🟡")

# স্টাইলিশ হেডার
st.title("🟡 XAU/USD Spot Gold: Live AI Analyzer")
st.write(f"ট্রেডিংভিউ ডাটা কানেক্টেড | সর্বশেষ আপডেট: {datetime.now().strftime('%H:%M:%S')}")

# ট্রেডিংভিউ কানেক্ট করার ফাংশন
@st.cache_resource
def connect_tradingview():
    return TvDatafeed()

tv = connect_tradingview()

def get_realtime_data():
    try:
        # সরাসরি TradingView থেকে XAUUSD স্পট প্রাইস আনা হচ্ছে
        # Exchange: FX_IDC (এটি সবচেয়ে নির্ভুল স্পট প্রাইস দেয়)
        df = tv.get_hist(symbol='XAUUSD', exchange='FX_IDC', interval=Interval.in_1_minute, n_bars=100)
        return df
    except Exception as e:
        return None

# ডাটা লোড করা
df = get_realtime_data()

if df is not None and not df.empty:
    # লেটেস্ট প্রাইস এবং মুভমেন্ট
    current_price = round(df['close'].iloc[-1], 2)
    price_change = round(current_price - df['close'].iloc[-2], 2)
    
    # ইন্ডিকেটর ক্যালকুলেশন (RSI এবং EMA)
    df['RSI'] = ta.rsi(df['close'], length=14)
    df['EMA_20'] = ta.ema(df['close'], length=20)
    
    last_rsi = round(df['RSI'].iloc[-1], 2)

    # ওপরের ড্যাশবোর্ড (Metrics)
    col1, col2, col3 = st.columns(3)
    col1.metric("Live Gold Price", f"${current_price}", f"{price_change} USD")
    col2.metric("RSI (14)", last_rsi)
    col3.metric("Market Status", "Open" if price_change != 0 else "Closed")

    st.divider()

    # --- এআই স্মার্ট সিগন্যাল লজিক ---
    st.subheader("🤖 TradingView AI Signal")
    
    if last_rsi < 30:
        st.success("🚀 **STRONG BUY SIGNAL!** গোল্ড এখন সস্তা (Oversold), দাম বাড়ার সম্ভাবনা প্রবল।")
        st.balloons()
    elif last_rsi > 70:
        st.error("📉 **STRONG SELL SIGNAL!** গোল্ড এখন দামী (Overbought), দাম কমার সম্ভাবনা বেশি।")
    elif 30 <= last_rsi <= 40:
        st.info("⚖️ **WAIT FOR BUY:** মার্কেট নিচে নামছে, ৩-এর নিচে RSI গেলে কিনুন।")
    elif 60 <= last_rsi <= 70:
        st.info("⚖️ **WAIT FOR SELL:** মার্কেট উপরে উঠছে, ৭০-এর উপরে RSI গেলে বেচুন।")
    else:
        st.warning("⚖️ **NEUTRAL:** এখন কোনো বড় মুভমেন্ট নেই। স্ক্যাল্পিং এড়িয়ে চলুন।")

    # --- ট্রেডিংভিউ ক্যান্ডেলস্টিক চার্ট ---
    st.subheader("📊 Live TradingView Chart (1m)")
    fig = go.Figure(data=[go.Candlestick(x=df.index,
                open=df['open'], high=df['high'],
                low=df['low'], close=df['close'], name='Price')])
    
    # EMA ট্রেন্ড লাইন যোগ করা
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='yellow', width=1), name='EMA 20'))
    
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=600,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("ট্রেডিংভিউ সার্ভারের সাথে কানেক্ট করা যাচ্ছে না। দয়া করে ১ মিনিট পর রিফ্রেশ দিন।")

st.caption("সতর্কতা: এটি সরাসরি TradingView FX_IDC থেকে ডাটা নিচ্ছে। ট্রেড করার আগে নিজের রিস্ক ম্যানেজমেন্ট যাচাই করুন।")