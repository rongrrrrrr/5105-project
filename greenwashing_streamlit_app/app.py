
import streamlit as st
import tempfile
import os
from greenwashing_radar_analysis_updated import evaluate_pdf_with_gemini, plot_radar

# Set up Streamlit page
st.set_page_config(page_title="Greenwashing Detection System", layout="centered")
st.title("🌿 Greenwashing Detection & Scoring System")

# Input Gemini API key
api_key = st.text_input("🔑 Enter your Gemini API Key", type="password")
os.environ["GOOGLE_API_KEY"] = api_key

# Upload PDF file
uploaded_file = st.file_uploader("📄 Upload an ESG PDF report", type=["pdf"])

if uploaded_file and st.button("🚀 Run Analysis"):
    with st.spinner("Analyzing document..."):
        # Save uploaded file to a temporary path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_path = tmp_file.name

        # Call backend function from original logic
        df = evaluate_pdf_with_gemini(temp_path)

        # Extract average scores
        avg_scores = df[["透明度", "具体性", "完整性", "一致性"]].mean().to_dict()

        # Plot and display radar chart
        st.subheader("📊 ESG Radar Chart")
        fig = plot_radar(avg_scores)
        st.pyplot(fig)

        # Show detailed score table
        st.subheader("📋 Detailed Scoring Table")
        st.dataframe(df)
