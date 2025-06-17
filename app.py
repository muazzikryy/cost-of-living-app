
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Cost of Living Estimator", layout="wide")

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("cost-of-living.csv")

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
components = ['Food & Restaurants', 'Groceries', 'Transportation', 'Utilities & Lifestyle', 'Education', 'Housing']

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🧮 Custom Estimate", "🔁 Compare Cities"])

# Tab 1: Overview
with tab1:
    st.title("🌍 Cost of Living Estimator")
    country = st.sidebar.selectbox("Select Country", sorted(df['country'].unique()))
    city = st.sidebar.selectbox("Select City", sorted(df[df['country'] == country]['city'].unique()))
    city_data = df[(df['country'] == country) & (df['city'] == city)]

    if not city_data.empty:
        st.subheader(f"📊 Cost of Living Breakdown in {city}, {country}")
        values = city_data[components].values[0]
        st.bar_chart(pd.Series(values, index=components))

        col1, col2 = st.columns(2)
        col1.metric("💵 Estimated Cost of Living (USD)", f"{city_data['CostOfLiving'].values[0]:,.2f}")
        col2.metric("📈 Cost-to-Income Ratio", f"{city_data['CostToIncomeRatio'].values[0]:.2f}")
        st.info(f"💼 Income Tier: **{city_data['IncomeTier'].values[0]}**")

# Tab 2: Custom Estimate
with tab2:
    st.title("🧮 Custom Living Cost Estimator")
    st.write("Enter your estimated monthly expenses:")

    income = st.number_input("Monthly Net Income (USD)", min_value=100, value=3000)
    custom_inputs = {
        'Housing': st.number_input("Housing", value=1000),
        'Food & Restaurants': st.number_input("Food & Restaurants", value=400),
        'Groceries': st.number_input("Groceries", value=300),
        'Transportation': st.number_input("Transportation", value=200),
        'Utilities & Lifestyle': st.number_input("Utilities & Lifestyle", value=150),
        'Education': st.number_input("Education", value=100),
    }

    if st.button("Calculate Estimate"):
        total_cost = (
            0.4 * custom_inputs['Housing'] +
            0.1 * custom_inputs['Food & Restaurants'] +
            0.1 * custom_inputs['Groceries'] +
            0.15 * custom_inputs['Transportation'] +
            0.1 * custom_inputs['Utilities & Lifestyle'] +
            0.15 * custom_inputs['Education']
        )
        ratio = total_cost / income
        st.success(f"Estimated Cost of Living: ${total_cost:,.2f}")
        st.info(f"Cost-to-Income Ratio: {ratio:.2f}")
        if ratio > 1:
            st.warning("⚠️ This lifestyle exceeds your income!")
        elif ratio > 0.6:
            st.warning("⚠️ This lifestyle may be tight on your budget.")
        else:
            st.success("✅ Your lifestyle appears financially manageable.")

# Tab 3: Compare Cities
with tab3:
    st.title("🔁 Compare Two Cities")
    col1, col2 = st.columns(2)
    with col1:
        country1 = st.selectbox("Select Country A", sorted(df['country'].unique()), key='c1')
        city1 = st.selectbox("Select City A", sorted(df[df['country'] == country1]['city'].unique()), key='city1')
    with col2:
        country2 = st.selectbox("Select Country B", sorted(df['country'].unique()), key='c2')
        city2 = st.selectbox("Select City B", sorted(df[df['country'] == country2]['city'].unique()), key='city2')

    data1 = df[(df['country'] == country1) & (df['city'] == city1)]
    data2 = df[(df['country'] == country2) & (df['city'] == city2)]

    if not data1.empty and not data2.empty:
        st.write(f"### {city1}, {country1} vs. {city2}, {country2}")
        comp_data = pd.DataFrame({
            f"{city1}": data1[components + ['CostOfLiving']].values[0],
            f"{city2}": data2[components + ['CostOfLiving']].values[0]
        }, index=components + ['Total'])

        st.dataframe(comp_data.style.format("${:.2f}"))
        st.bar_chart(comp_data)
