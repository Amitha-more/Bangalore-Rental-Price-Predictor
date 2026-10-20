
import html

import streamlit as st

from src import unified_prediction_engine


# ==================================================
# PAGE SETTINGS
# ==================================================

st.set_page_config(
    page_title="Bangalore Rental Price Predictor",
    page_icon="🏠",
    layout="centered",
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown(
    """
    <style>

    /* Main page */
    .stApp {
        background-color: #f7f7f5;
    }

    /* Main content width */
    .block-container {
        max-width: 850px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* Title */
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }

    /* Subtitle */
    .subtitle {
        color: #555555;
        font-size: 1rem;
        line-height: 1.5;
        margin-bottom: 1.8rem;
    }

    /* Cards */
    .card {
        background: white;
        border: 1px solid #dddddd;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Section heading */
    .section-heading {
        font-size: 1.05rem;
        font-weight: 650;
        margin-bottom: 1rem;
    }

    /* Result heading */
    .result-label {
        font-size: 0.95rem;
        color: #555555;
        margin-bottom: 0.4rem;
    }

    /* Large rent */
    .rent-range {
        font-size: 2.3rem;
        font-weight: 750;
        line-height: 1.15;
        margin-bottom: 0.5rem;
    }

    /* Supporting text */
    .supporting-text {
        color: #666666;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* SHAP row */
    .shap-row {
        margin-bottom: 1rem;
    }

    .shap-header {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 0.3rem;
        font-size: 0.9rem;
    }

    .shap-feature {
        font-weight: 600;
    }

    .shap-value-positive {
        color: #333333;
        white-space: nowrap;
    }

    .shap-value-negative {
        color: #666666;
        white-space: nowrap;
    }

    .bar-track {
        width: 100%;
        height: 9px;
        background: #eeeeee;
        border-radius: 999px;
        overflow: hidden;
    }

    .bar-positive {
        height: 100%;
        background: #333333;
        border-radius: 999px;
    }

    .bar-negative {
        height: 100%;
        background: #999999;
        border-radius: 999px;
    }

    /* Disclaimer */
    .disclaimer {
        color: #777777;
        font-size: 0.78rem;
        line-height: 1.55;
        margin-top: 1rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# HEADER
# ==================================================

st.markdown(
    '<div class="main-title">Bangalore Rental Price Predictor</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        Enter the details of an apartment to estimate an approximate
        fair monthly rent range, compare it with collected market listings,
        and understand what drives the model's estimate.
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# APARTMENT INPUTS
# ==================================================

st.markdown(
    '<div class="card">',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-heading">Apartment details</div>',
    unsafe_allow_html=True,
)

with st.form("prediction_form"):

    locality = st.selectbox(
        "Locality",
        [
            "Whitefield",
            "Koramangala",
            "HSR Layout",
            "Indiranagar",
            "Electronic City",
            "Marathahalli",
        ],
    )

    size_sqft = st.number_input(
        "Size (sq ft)",
        min_value=250,
        max_value=5700,
        value=1200,
        step=50,
    )

    bhk = st.number_input(
        "BHK",
        min_value=1,
        max_value=4,
        value=2,
        step=1,
    )

    bathrooms = st.number_input(
        "Bathrooms",
        min_value=1,
        max_value=5,
        value=2,
        step=1,
    )

    furnishing_status = st.selectbox(
        "Furnishing",
        [
            "Unfurnished",
            "Semi-Furnished",
            "Furnished",
        ],
    )

    predict_button = st.form_submit_button(
        "Predict rent",
        use_container_width=True,
    )

st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


# ==================================================
# RUN THE PREDICTION
# ==================================================

if predict_button:

    with st.spinner("Estimating rent and checking market comparables..."):

        result = unified_prediction_engine.get_rental_assessment(
            locality=locality,
            size_sqft=size_sqft,
            bhk=bhk,
            bathrooms=bathrooms,
            furnishing_status=furnishing_status,
        )

    # --------------------------------------------------
    # MACHINE-LEARNING RESULTS
    # --------------------------------------------------

    prediction = result["ml_prediction"]
    lower_rent = result["ml_lower_rent"]
    upper_rent = result["ml_upper_rent"]
    explanation = result["shap_explanation"]

    # --------------------------------------------------
    # CURRENT-MARKET RESULTS
    # --------------------------------------------------

    market_median = result["market_median_rent"]
    market_q1 = result["market_q1_rent"]
    market_q3 = result["market_q3_rent"]

    market_count = result["market_listing_count"]
    furnishing_count = result["market_furnishing_listing_count"]

    comparison_type = result["market_comparison_type"]
    sample_quality = result["market_sample_quality"]

    furnishing_breakdown = result["market_furnishing_breakdown"]
    data_refreshed = result["market_data_refreshed"]

    comparison_to_market = result["comparison_to_market"]


    # ==================================================
    # MACHINE-LEARNING RESULT CARD
    # ==================================================

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-heading">Your estimated rent</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="result-label">Approximate monthly rent range</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="rent-range">
            ₹{lower_rent:,.0f} – ₹{upper_rent:,.0f}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="supporting-text">
            Model estimate: ₹{prediction:,.0f} per month
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="supporting-text">
            This estimate comes from the machine-learning model trained
            on historical rental data.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


    # ==================================================
    # CURRENT MARKET REFERENCE CARD
    # ==================================================

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-heading">Current market reference</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="supporting-text">
            Based on the latest saved snapshot of collected NoBroker
            asking-rent listings. This is a market comparison, not a
            guaranteed live feed.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if market_median is not None:

        # Display Q1–Q3 only when both values are available.
        if market_q1 is not None and market_q3 is not None:

            st.markdown(
                '<div class="result-label">'
                'Middle 50% of comparable asking rents (Q1–Q3)'
                '</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="rent-range">
                    ₹{market_q1:,.0f} – ₹{market_q3:,.0f}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="supporting-text">
                Median comparable asking rent:
                <strong>₹{market_median:,.0f} per month</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write(f"Comparable listings used: {market_count}")
        st.write(
            f"Listings matching the selected furnishing status: "
            f"{furnishing_count}"
        )

        st.write(f"Comparison method: {comparison_type}")
        st.write(f"Sample quality: {sample_quality}")

        # Furnishing mix of the comparable listings
        if furnishing_breakdown:

            st.markdown("**Furnishing breakdown of comparable listings**")

            for status, count in furnishing_breakdown.items():
                st.write(f"- {status}: {count}")

        # Compare the model estimate with the market median
        if comparison_to_market:

            st.markdown(
                f"""
                <div class="supporting-text">
                    <strong>Model estimate vs. market:</strong>
                    {html.escape(str(comparison_to_market))}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Display the snapshot timestamp, if provided by the engine
        if data_refreshed:

            st.caption(
                f"Market data snapshot timestamp: {data_refreshed}"
            )

        if sample_quality == "Very limited":

            st.warning(
                "Very few comparable listings were available. "
                "Treat the market reference as a rough indication."
            )

        elif sample_quality == "Limited":

            st.info(
                "The market comparison uses a limited number of listings. "
                "The median and quartiles may change as more data is collected."
            )

    else:

        st.warning(
            "No suitable current-market comparables were found for this "
            "combination of locality, BHK, apartment size, and furnishing. "
            "The machine-learning estimate above is still available."
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


    # ==================================================
    # SHAP EXPLANATION CARD
    # ==================================================

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-heading">Why this estimate?</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="supporting-text">
            These values show how each apartment feature contributes
            to the model's estimate. Positive values push the estimate
            upward; negative values push it downward.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if explanation is not None and not explanation.empty:

        max_contribution = explanation["absolute_contribution"].max()

        if max_contribution == 0:
            max_contribution = 1

        for _, row in explanation.iterrows():

            feature = html.escape(str(row["feature"]))

            contribution = float(row["contribution"])
            absolute_contribution = float(row["absolute_contribution"])

            width = (
                absolute_contribution / max_contribution * 100
            )

            if contribution >= 0:

                value_text = f"+₹{contribution:,.0f}"
                value_class = "shap-value-positive"
                bar_class = "bar-positive"

            else:

                value_text = f"-₹{abs(contribution):,.0f}"
                value_class = "shap-value-negative"
                bar_class = "bar-negative"

            shap_html = f"""<div class="shap-row">
<div class="shap-header">
<span class="shap-feature">{feature}</span>
<span class="{value_class}">{value_text}</span>
</div>
<div class="bar-track">
<div class="{bar_class}" style="width: {width:.1f}%"></div>
</div>
</div>"""

            st.markdown(
                shap_html,
                unsafe_allow_html=True,
            )

    else:

        st.info(
            "A feature explanation is not available for this prediction."
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ==================================================
# FOOTER / DISCLAIMER
# ==================================================

st.markdown(
    """
    <div class="disclaimer">
        <strong>Important:</strong> The machine-learning model uses
        historical rental data from selected Bangalore localities.
        Its estimated range is approximate and is based on historical
        validation errors; it is not a formal confidence interval,
        guaranteed fair price, or property valuation.

        The market reference uses collected NoBroker asking-rent listings
        from the latest saved data snapshot. These are advertised asking
        prices, not confirmed rental transaction prices. The data is not
        fetched automatically in real time, and comparable listings may
        be limited for some localities, apartment sizes, BHK types, or
        furnishing statuses. Always verify current prices independently.
    </div>
    """,
    unsafe_allow_html=True,
)
