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
        ax.hist(df[selected_column], bins=num_bins, range=hist_range, edgecolor='black')  # Added edgecolor='black'
        ax.set_xlabel(selected_column)
        ax.set_ylabel("Frequency")
        ax.set_title(f"Histogram of {selected_column}")
        st.pyplot(fig)

        # Descriptive Statistics
        st.subheader("Descriptive Statistics")
        selected_series = df[selected_column]
        st.write(f"**Max:** {selected_series.max()}")
        st.write(f"**Min:** {selected_series.min()}")
        st.write(f"**Mode:** {selected_series.mode().iloc[0] if not selected_series.mode().empty else 'No unique mode'}")
        st.write(f"**Median:** {selected_series.median()}")
        st.write(f"**Average (Mean):** {selected_series.mean()}")
        st.write(f"**Standard Deviation:** {selected_series.std()}")
        st.write("**Quartiles:**")
        st.write(selected_series.quantile([0.25, 0.50, 0.75]))

    else:
        st.warning("No numerical columns found in the uploaded CSV file.")
else:
    st.info("Upload a CSV file to begin exploring histograms.")
