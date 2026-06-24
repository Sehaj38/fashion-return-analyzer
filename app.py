import streamlit as st
import pandas as pd
from data_processor import load_reviews, get_reviews_text
from analyzer import analyze_reviews

st.set_page_config(
    page_title="Return Analyser",
    layout="wide"
)

st.title("Fashion Return Reduction Analyser")
st.markdown("Upload customer reviews and get **AI-powered insights** to reduce product returns.")
st.divider()

st.subheader("Step 1: Upload Your Reviews CSV")

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type="csv",
    help="CSV must contain columns: product_name, review, rating"
)

if uploaded_file is not None:
    df = load_reviews(uploaded_file)

    st.success(f"Successfully loaded {len(df)} reviews!")

    with st.expander("View Raw Data"):
        st.dataframe(df, width='stretch')

    st.divider()

    st.subheader("Step 2: Analyze With AI")

    if st.button("Analyze Reviews", type="primary", width='stretch'):
        with st.spinner("AI is analyzing reviews..."):
            reviews_text = get_reviews_text(df)
            analysis = analyze_reviews(reviews_text)

        st.divider()
        st.subheader("Analysis Results")
        st.markdown(analysis)

else:
    st.info("Please upload a CSV file to get started.")