import streamlit as st
import pandas as pd
from data_processor import load_reviews, get_reviews_text
from analyzer import analyze_reviews


st.set_page_config(
    page_title="Fashion Return Analyzer",
    layout="wide"
)


st.markdown("""
    <style>
    .risk-high { 
        background-color: #ff4b4b22; 
        border-left: 5px solid #ff4b4b; 
        padding: 15px; 
        border-radius: 5px;
    }
    .risk-medium { 
        background-color: #ffa50022; 
        border-left: 5px solid #ffa500; 
        padding: 15px; 
        border-radius: 5px;
    }
    .risk-low { 
        background-color: #00c85322; 
        border-left: 5px solid #00c853; 
        padding: 15px; 
        border-radius: 5px;
    }
    .complaint-card {
        background-color: #1e1e2e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #333;
    }
    .recommendation-card {
        background-color: #1e2e1e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)


st.title("Fashion Return Reduction Analyzer")
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

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Reviews", len(df))
    with col2:
        if 'rating' in df.columns:
            avg = round(df['rating'].mean(), 2)
            st.metric("Average Rating", f"{avg} / 5")
    with col3:
        if 'rating' in df.columns:
            low = len(df[df['rating'] <= 2])
            st.metric("Low Ratings (≤2)", low)

    with st.expander("View Raw Data"):
        st.dataframe(df, width='stretch')

    st.divider()

    st.subheader("Step 2: Analyze With AI")

    if st.button("Analyze Reviews", type="primary", width='stretch'):
        with st.spinner("AI is analyzing your reviews..."):
            reviews_text = get_reviews_text(df)
            result = analyze_reviews(reviews_text)

        st.divider()
        st.subheader("Analysis Results")

        st.info(f"**Summary:** {result['summary']}")

        st.divider()

        st.subheader("Return Risk Assessment")

        risk = result['return_risk']
        level = risk['level']
        score = risk['score']
        reason = risk['reason']

        if level == "High":
            risk_class = "risk-high"
            emoji = "🔴"
        elif level == "Medium":
            risk_class = "risk-medium"
            emoji = "🟡"
        else:
            risk_class = "risk-low"
            emoji = "🟢"

        st.markdown(f"""
            <div class="{risk_class}">
                <h3>{emoji} Return Risk: {level} ({score}%)</h3>
                <p>{reason}</p>
            </div>
        """, unsafe_allow_html=True)

        # Progress bar as visual risk meter
        st.progress(score / 100)

        st.divider()

        # ── Two Column Layout ──
        left, right = st.columns(2)

        # ── Complaints ──
        with left:
            st.subheader("Top Complaints")
            for i, complaint in enumerate(result['top_complaints']):
                st.markdown(f"""
                    <div class="complaint-card">
                        <strong>#{i+1} {complaint['complaint']}</strong>
                        <p style="color:#aaa; margin-top:5px;">{complaint['description']}</p>
                    </div>
                """, unsafe_allow_html=True)

        # ── Recommendations ──
        with right:
            st.subheader("Recommendations")
            for i, rec in enumerate(result['recommendations']):
                st.markdown(f"""
                    <div class="recommendation-card">
                        <strong>#{i+1} {rec['title']}</strong>
                        <p style="color:#aaa; margin-top:5px;">{rec['action']}</p>
                    </div>
                """, unsafe_allow_html=True)

else:
    st.info("Please upload a CSV file to get started.")