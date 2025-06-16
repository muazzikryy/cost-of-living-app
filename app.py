
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Cost of Living Estimator", layout="wide")

# Title
st.title("🌍 Cost of Living Estimator")

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("cost-of-living.csv")

    # Clean steps (simplified — copy full logic from your Colab if needed)
    df.dropna(thresh=df.shape[1]-22, inplace=True)
    cols_to_fill = [f'x{i}' for i in range(1, 56)]
    for col in cols_to_fill:
        df[col] = df.groupby('country')[col].transform(lambda x: x.fillna(x.median()))
    df[cols_to_fill] = df[cols_to_fill].fillna(df[cols_to_fill].mean())

    df.drop(['x28', 'x30', 'x32', 'x34', 'x37', 'x38', 'x44','x45','x46','x47','x48','x49','x51', 'x53','x55'], axis=1, inplace=True)
    df.drop_duplicates(inplace=True)

    df['Food & Restaurants'] = df['x1'] + df['x2'] + df['x3'] + df['x4'] + df['x5'] + df['x6'] + df['x7'] + df['x8']
    df['Groceries'] = df['x9'] + df['x10'] + df['x11'] + df['x12'] + df['x13'] + df['x14'] + df['x15'] + df['x16'] + df['x17'] + df['x18'] + df['x19'] + df['x20'] + df['x21'] + df['x22'] + df['x23'] + df['x24'] + df['x25'] + df['x26'] + df['x27']
    df['Transportation'] = df['x29'] + df['x31'] + df['x33'] + df['x35'] / 12
    df['Utilities & Lifestyle'] = df['x36'] + df['x39'] + df['x40'] + df['x41']
    df['Education'] = df['x42'] + df['x43'] / 12
    df['Housing'] = df['x50'] + df['x52']
    df['Income & Finance'] = df['x54']

    df['CostOfLiving'] = (
        0.4 * df['Housing'] +
        0.1 * df['Food & Restaurants'] +
        0.1 * df['Groceries'] +
        0.15 * df['Transportation'] +
        0.1 * df['Utilities & Lifestyle'] +
        0.15 * df['Education']
    )

    df['CostToIncomeRatio'] = df['CostOfLiving'] / df['Income & Finance']
    df['IncomeTier'] = pd.qcut(df['Income & Finance'], q=3, labels=['Low', 'Medium', 'High'])

    return df

df = load_data()

# Sidebar filters
country = st.sidebar.selectbox("Select Country", sorted(df['country'].unique()))
city = st.sidebar.selectbox("Select City", sorted(df[df['country'] == country]['city'].unique()))

city_data = df[(df['country'] == country) & (df['city'] == city)]

if not city_data.empty:
    st.subheader(f"📊 Cost of Living Breakdown in {city}, {country}")

    components = ['Food & Restaurants', 'Groceries', 'Transportation', 'Utilities & Lifestyle', 'Education', 'Housing']
    values = city_data[components].values[0]

    st.bar_chart(pd.Series(values, index=components))

    col1, col2 = st.columns(2)
    col1.metric("💵 Estimated Cost of Living (USD)", f"{city_data['CostOfLiving'].values[0]:,.2f}")
    col2.metric("📈 Cost-to-Income Ratio", f"{city_data['CostToIncomeRatio'].values[0]:.2f}")

    st.info(f"💼 Income Tier: **{city_data['IncomeTier'].values[0]}**")
else:
    st.warning("No data found for selected city/country.")
