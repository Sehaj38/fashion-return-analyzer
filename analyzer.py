from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

def setup_groq():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Check your .env file")
    client = Groq(api_key=api_key)
    return client

def analyze_reviews(reviews_text):
    prompt = f"""
    You are a Senior E-commerce Product Analytics AI working for a large fashion retailer.
    Your goal is to identify the key drivers of product returns from customer reviews and provide actionable business recommendations.

    Analyze the customer reviews and generate a comprehensive return-risk report.

    ## Tasks

    ### 1. Executive Summary

    Provide a 2-3 sentence summary of the overall customer sentiment and major concerns.

    ### 2. Return Risk Score

    Estimate the likelihood that this product will experience high return rates.

    Return Risk Score: X/100

    Classification:

    * Low Risk (0-39)
    * Medium Risk (40-69)
    * High Risk (70-100)

    Provide a brief justification.

    ### 3. Complaint Analysis

    Identify the most common customer complaints.

    For each complaint provide:

    * Complaint Category
    * Frequency (Low / Medium / High)
    * Example Evidence from Reviews

    Possible Categories:

    * Size & Fit
    * Color Mismatch
    * Fabric Quality
    * Comfort
    * Stitching Issues
    * Product Durability
    * Product Description Mismatch
    * Delivery Issues
    * Quality Control
    * Other

    ### 4. Positive Signals

    Identify the top positive aspects customers mention.

    For each provide:

    * Positive Category
    * Frequency
    * Supporting Evidence

    ### 5. Root Cause Analysis

    Determine the main reasons likely causing product returns.

    Rank them in order of impact.

    Example:

    1. Size inconsistency
    2. Product-image mismatch
    3. Fabric quality concerns

    ### 6. Business Recommendations

    Provide 5 actionable recommendations that a fashion retailer can implement to reduce returns.

    Examples:

    * Improve size chart accuracy
    * Add customer body-type information
    * Include additional product images
    * Improve fabric descriptions
    * Add fit recommendations

    ### 7. Priority Actions

    List the top 3 actions that should be implemented immediately.

    ### 8. Output Format

    Return your response in the following structure:

    EXECUTIVE SUMMARY
    RETURN RISK SCORE
    TOP COMPLAINTS
    POSITIVE SIGNALS
    ROOT CAUSE ANALYSIS
    BUSINESS RECOMMENDATIONS
    PRIORITY ACTIONS
    Customer Reviews:
    {reviews_text}
    """
    client = setup_groq()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content