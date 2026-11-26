# ============================================================
# PHASE 6: INTERACTIVE RETAIL ANALYTICS DASHBOARD
# PROJECT: RETAIL MARKET BASKET & CUSTOMER RFM DASHBOARD
# ============================================================


# STEP 1: IMPORT REQUIRED LIBRARIES

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# STEP 2: PAGE CONFIGURATION

st.set_page_config(
    page_title="Retail Analytics Dashboard",
    page_icon="🛒",
    layout="wide"
)


# STEP 3: DASHBOARD TITLE

st.title("🛒 Retail Market Basket & Customer RFM Dashboard")

st.markdown(
    "An interactive retail analytics application "
    "for sales analysis, customer segmentation "
    "and product association discovery."
)

st.divider()


# STEP 4: LOAD DATASETS

@st.cache_data
def load_data():

    # Load cleaned retail data
    sales_df = pd.read_csv("cleaned_retail.csv")

    # Load customer data
    customer_df = pd.read_csv("cleaned_customer_retail.csv")

    # Load RFM results
    rfm_df = pd.read_csv("rfm_customers.csv")

    # Load association rules
    rules_df = pd.read_csv("association_rules.csv")

    # Convert date column
    sales_df["InvoiceDate"] = pd.to_datetime(
        sales_df["InvoiceDate"]
    )

    customer_df["InvoiceDate"] = pd.to_datetime(
        customer_df["InvoiceDate"]
    )

    return sales_df, customer_df, rfm_df, rules_df


try:

    sales_df, customer_df, rfm_df, rules_df = load_data()

except FileNotFoundError as error:

    st.error(
        f"Required file not found: {error.filename}. "
        "Please run the previous project phases first."
    )

    st.stop()


# STEP 5: SIDEBAR FILTERS

st.sidebar.header("Dashboard Filters")

# Country selection

countries = sorted(sales_df["Country"].dropna().unique())

selected_country = st.sidebar.selectbox(
    "Select Country",
    ["All Countries"] + countries
)


# Date selection

min_date = sales_df["InvoiceDate"].min().date()
max_date = sales_df["InvoiceDate"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(selected_dates, (tuple, list)):

    if len(selected_dates) == 2:

        start_date, end_date = selected_dates

    else:

        start_date = selected_dates[0]
        end_date = selected_dates[0]

else:

    start_date = selected_dates
    end_date = selected_dates


# STEP 6: FILTER SALES DATA

filtered_df = sales_df[
    (sales_df["InvoiceDate"].dt.date >= start_date)
    &
    (sales_df["InvoiceDate"].dt.date <= end_date)
].copy()


if selected_country != "All Countries":

    filtered_df = filtered_df[
        filtered_df["Country"] == selected_country
    ]


# Filter customer data using the same conditions

filtered_customers = customer_df[
    (customer_df["InvoiceDate"].dt.date >= start_date)
    &
    (customer_df["InvoiceDate"].dt.date <= end_date)
].copy()


if selected_country != "All Countries":

    filtered_customers = filtered_customers[
        filtered_customers["Country"] == selected_country
    ]


# STEP 7: CALCULATE KEY PERFORMANCE INDICATORS

total_revenue = filtered_df["Revenue"].sum()

total_orders = filtered_df["InvoiceNo"].nunique()

total_customers = filtered_customers["CustomerID"].nunique()

total_products = filtered_df["Description"].nunique()


# STEP 8: DISPLAY KPI CARDS

st.header("📊 Business Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Revenue",
    f"£{total_revenue:,.2f}"
)

col2.metric(
    "Total Orders",
    f"{total_orders:,}"
)

col3.metric(
    "Total Customers",
    f"{total_customers:,}"
)

col4.metric(
    "Total Products",
    f"{total_products:,}"
)

st.divider()


# STEP 9: SALES ANALYSIS

st.header("📈 Sales Analysis")

if filtered_df.empty:

    st.warning("No sales data available for the selected filters.")

else:

    # Monthly revenue

    filtered_df["Month"] = (
        filtered_df["InvoiceDate"].dt.to_period("M").astype(str)
    )

    monthly_sales = (
        filtered_df.groupby("Month")["Revenue"]
        .sum()
        .reset_index()
    )

    fig1 = px.line(
        monthly_sales,
        x="Month",
        y="Revenue",
        markers=True,
        title="Monthly Revenue Trend"
    )

    fig1.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue (£)"
    )

    st.plotly_chart(
        fig1,
        use_container_width=True
    )


    # Country-wise revenue

    country_sales = (
        filtered_df.groupby("Country")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig2 = px.bar(
        country_sales,
        x="Country",
        y="Revenue",
        title="Top 10 Countries by Revenue"
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


st.divider()


# STEP 10: PRODUCT ANALYSIS

st.header("📦 Product Analysis")

if filtered_df.empty:

    st.info("No product data available for the selected filters.")

else:

    col1, col2 = st.columns(2)

    # Top-selling products

    with col1:

        top_products = (
            filtered_df.groupby("Description")["Quantity"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig3 = px.bar(
            top_products,
            x="Quantity",
            y="Description",
            orientation="h",
            title="Top 10 Selling Products"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )


    # Frequently purchased products

    with col2:

        frequent_products = (
            filtered_df.groupby("Description")["InvoiceNo"]
            .nunique()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig4 = px.bar(
            frequent_products,
            x="InvoiceNo",
            y="Description",
            orientation="h",
            title="Top 10 Frequently Purchased Products"
        )

        st.plotly_chart(
            fig4,
            use_container_width=True
        )


st.divider()


# STEP 11: CUSTOMER RFM ANALYSIS

st.header("👥 Customer Segmentation")

if "Customer_Segment" in rfm_df.columns:

    segment_counts = (
        rfm_df["Customer_Segment"]
        .value_counts()
        .reset_index()
    )

    segment_counts.columns = [
        "Customer Segment",
        "Number of Customers"
    ]

    col1, col2 = st.columns(2)

    with col1:

        fig5 = px.pie(
            segment_counts,
            names="Customer Segment",
            values="Number of Customers",
            title="Customer Segment Distribution",
            hole=0.4
        )

        st.plotly_chart(
            fig5,
            use_container_width=True
        )

    with col2:

        fig6 = px.bar(
            segment_counts,
            x="Customer Segment",
            y="Number of Customers",
            title="Customers in Each Segment"
        )

        st.plotly_chart(
            fig6,
            use_container_width=True
        )

    # Display RFM table

    st.subheader("Customer RFM Details")

    st.dataframe(
        rfm_df.head(20),
        use_container_width=True
    )

else:

    st.warning("Customer segmentation column is missing.")


st.divider()


# STEP 12: MARKET BASKET ANALYSIS

st.header(" Market Basket Analysis")

st.write(
    "Discover products that customers frequently purchase together "
    "using the Apriori algorithm."
)

if not rules_df.empty:

    # Sort rules according to lift

    rules_display = rules_df.sort_values(
        by="lift",
        ascending=False
    ).head(20)

    # Display association rules

    st.subheader("Top Product Association Rules")

    st.dataframe(
        rules_display[
            [
                "antecedents",
                "consequents",
                "support",
                "confidence",
                "lift"
            ]
        ],
        use_container_width=True
    )

    # Association rule visualization

    fig7 = px.bar(
        rules_display.head(10),
        x="lift",
        y="antecedents",
        color="confidence",
        orientation="h",
        title="Top Product Associations"
    )

    st.plotly_chart(
        fig7,
        use_container_width=True
    )

else:

    st.warning("No association rules are available.")


st.divider()


# STEP 13: PROJECT INFORMATION

st.header("ℹ About This Project")

st.markdown(
    """
    **Project Title:** Retail Market Basket & Customer RFM Dashboard

    **Technologies Used:**
    - Python
    - Pandas
    - NumPy
    - Matplotlib
    - Seaborn
    - Plotly
    - Streamlit
    - Mlxtend

    **Analytical Techniques:**
    - Exploratory Data Analysis
    - Customer RFM Analysis
    - Customer Segmentation
    - Market Basket Analysis
    - Apriori Algorithm
    - Association Rule Mining
    """
)


# STEP 14: FOOTER

st.divider()

st.caption(
    "Retail Market Basket & Customer RFM Dashboard | "
    "Developed using Python and Streamlit"
)

print("DASHBOARD APPLICATION CODE LOADED SUCCESSFULLY!")