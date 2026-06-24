import streamlit as st
import pandas as pd
import plotly.express as px

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
    padding: 15px; border-radius: 5px;
}
.risk-medium {
    background-color: #ffa50022;
    border-left: 5px solid #ffa500;
    padding: 15px; border-radius: 5px;
}
.risk-low {
    background-color: #00c85322;
    border-left: 5px solid #00c853;
    padding: 15px; border-radius: 5px;
}
.complaint-card {
    background-color: #1e1e2e;
    padding: 15px; border-radius: 10px;
    margin-bottom: 10px; border: 1px solid #333;
}
.recommendation-card {
    background-color: #1e2e1e;
    padding: 15px; border-radius: 10px;
    margin-bottom: 10px; border: 1px solid #333;
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
    help="CSV must contain a review column. rating and product_name are optional but recommended.",
)

if uploaded_file is not None:

    try:
        df = load_reviews(uploaded_file)
    except ValueError as e:
        st.error(f" Could not load file: {e}")
        st.stop()
    except Exception as e:
        st.error(f" Unexpected error reading file: {e}")
        st.stop()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Reviews", len(df))
    with col2:
        if 'rating' in df.columns and df['rating'].notna().any():
            avg = round(df['rating'].mean(), 2)
            st.metric("Average Rating", f"{avg} / 5")
        else:
            st.metric("Average Rating", "N/A")
    with col3:
        if 'rating' in df.columns and df['rating'].notna().any():
            low = int((df['rating'] <= 2).sum())
            st.metric("Low Ratings (≤ 2)", low)
        else:
            st.metric("Low Ratings (≤ 2)", "N/A")

    with st.expander("View Raw Data"):
        st.dataframe(df, width='stretch')

    st.divider()

    st.subheader("Step 2: Analyze With AI")


    @st.cache_data(show_spinner=False)
    def run_analysis(file_name: str, n_rows: int, reviews_text: str) -> dict:
        return analyze_reviews(reviews_text)


    if st.button("Analyze Reviews", type="primary", width='stretch'):

        with st.spinner("AI is analyzing your reviews..."):
            reviews_text = get_reviews_text(df)
            try:
                result = run_analysis(uploaded_file.name, len(df), reviews_text)
            except RuntimeError as e:
                st.error(f"AI service error: {e}")
                st.stop()
            except ValueError as e:
                st.error(f"AI returned an unexpected response: {e}")
                st.stop()
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()

        st.divider()
        st.subheader("Analysis Results")

        st.info(f"**Summary:** {result['summary']}")
        st.divider()

        st.subheader("Return Risk Assessment")

        risk  = result['return_risk']
        level = risk['level']
        score = int(risk['score'])
        reason = risk['reason']

        if level == "High":
            risk_class = "risk-high"
            emoji      = "🔴"
            bar_color  = "#ff4b4b"
        elif level == "Medium":
            risk_class = "risk-medium"
            emoji      = "🟡"
            bar_color  = "#ffa500"
        else:
            risk_class = "risk-low"
            emoji      = "🟢"
            bar_color  = "#00c853"

        st.markdown(f"""
            <div class="{risk_class}">
                <h3>{emoji} Return Risk: {level} ({score}%)</h3>
                <p>{reason}</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background:#333; border-radius:10px; height:20px; margin-top:10px;">
                <div style="background:{bar_color}; width:{score}%;
                            height:20px; border-radius:10px;"></div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        left, right = st.columns(2)

        with left:
            st.subheader(" Top Complaints")
            for i, c in enumerate(result['top_complaints']):
                st.markdown(f"""
                    <div class="complaint-card">
                        <strong>#{i+1} {c['complaint']}</strong>
                        <p style="color:#aaa; margin-top:5px;">{c['description']}</p>
                    </div>
                """, unsafe_allow_html=True)

        with right:
            st.subheader(" Recommendations")
            for i, rec in enumerate(result['recommendations']):
                st.markdown(f"""
                    <div class="recommendation-card">
                        <strong>#{i+1} {rec['title']}</strong>
                        <p style="color:#aaa; margin-top:5px;">{rec['action']}</p>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()

        st.subheader(" Complaint Severity Chart")

        complaints = result['top_complaints']
        n = len(complaints) 

        chart_df = pd.DataFrame({
            'Complaint':      [c['complaint'] for c in complaints],
            'Severity Index': list(range(n, 0, -1)),
        })

        fig = px.bar(
            chart_df,
            x='Severity Index',
            y='Complaint',
            orientation='h',
            color='Severity Index',
            color_continuous_scale=['#00c853', '#ffa500', '#ff4b4b'],
            title="Top Complaints by Severity (left = most severe)",
        )
        fig.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            height=max(400, n * 60), 
        )
        fig.update_xaxes(showticklabels=False, title=None)
        fig.update_yaxes(title=None)

        st.plotly_chart(fig, use_container_width=True)

else:
    st.info(" Please upload a CSV file to get started.")