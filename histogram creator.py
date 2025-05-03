import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Interactive Histogram Explorer")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Uploaded Data")
    st.dataframe(df.head())

    numerical_cols = df.select_dtypes(include=np.number).columns
    if not numerical_cols.empty:
        selected_column = st.selectbox("Select a numerical column to visualize:", numerical_cols)

        st.sidebar.header("Histogram Parameters")
        num_bins = st.sidebar.slider("Number of Bins:", min_value=5, max_value=50, value=10)
        data_min = df[selected_column].min()
        data_max = df[selected_column].max()
        hist_range = st.sidebar.slider("Histogram Range:", min_value=float(data_min), max_value=float(data_max), value=(float(data_min), float(data_max)))

        fig, ax = plt.subplots()
        ax.hist(df[selected_column], bins=num_bins, range=hist_range, edgecolor='black')
        ax.set_xlabel(selected_column)
        ax.set_ylabel("Frequency")
        ax.set_title(f"Histogram of {selected_column}")
        st.pyplot(fig)

        # Descriptive Statistics
        st.subheader("Descriptive Statistics")
        selected_series = df[selected_column]

        def format_decimal(value):
            if isinstance(value, float):
                return f"{value:.1f}"
            elif isinstance(value, pd.Series):
                return value.apply(lambda x: f"{x:.1f}" if isinstance(x, float) else x)
            return value

        st.write(f"**Max:** {format_decimal(selected_series.max())}")
        st.write(f"**Min:** {format_decimal(selected_series.min())}")
        mode_val = selected_series.mode()
        st.write(f"**Mode:** {format_decimal(mode_val.iloc[0] if not mode_val.empty else 'No unique mode')}")
        st.write(f"**Median:** {format_decimal(selected_series.median())}")
        st.write(f"**Average (Mean):** {format_decimal(selected_series.mean())}")
        st.write(f"**Standard Deviation:** {format_decimal(selected_series.std())}")
        st.write("**Quartiles:**")
        st.write(format_decimal(selected_series.quantile([0.25, 0.50, 0.75])))

        # Percentile Calculation
        st.sidebar.header("Percentile Calculator")
        percentile_to_calculate = st.sidebar.number_input("Enter a percentile (0-100):", min_value=0, max_value=100, value=50, step=1)
        if st.sidebar.button("Calculate Percentile"):
            percentile_value = selected_series.quantile(percentile_to_calculate / 100)
            st.write(f"**{percentile_to_calculate}th Percentile:** {format_decimal(percentile_value)}")

    else:
        st.warning("No numerical columns found in the uploaded CSV file.")
else:
    st.info("Upload a CSV file to begin exploring histograms.")
