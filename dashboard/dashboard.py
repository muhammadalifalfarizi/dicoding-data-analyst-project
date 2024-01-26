import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Helper Function


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_approved_at').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })

    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    return daily_orders_df


def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_category_name_english")[
        "product_id"].count().reset_index()
    sum_order_items_df.rename(columns={
        "product_id": "product_count"
    }, inplace=True)
    sum_order_items_df = sum_order_items_df.sort_values(
        by="product_count", ascending=False)

    return sum_order_items_df


def create_bystate_df(df):
    bystate_df = df.groupby(
        by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)

    return bystate_df


# Load Cleaned Data
file_path = 'dashboard/all_df.csv'
all_df = pd.read_csv(file_path)
datetime_columns = ["order_approved_at", "order_purchase_timestamp", "order_delivered_carrier_date",
                    "order_delivered_customer_date", "order_estimated_delivery_date"]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Filter Data
min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    st.title("E-Heisenberg Distro")

    st.image(
        "https://media.posterlounge.com/img/products/740000/735290/735290_poster.jpg")

    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) &
                 (all_df["order_approved_at"] <= str(end_date))]

# Call the functions with your DataFrame
daily_orders_df = create_daily_orders_df(all_df)
sum_order_items_df = create_sum_order_items_df(all_df)
bystate_df = create_bystate_df(all_df)

# Title
st.header("E-Heisenberg Distro Dashboard")
st.subheader("Daily Orders")

# Daily Orders
col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(
        daily_orders_df.revenue.sum(), "IDR", locale='id_ID')
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Product Performance
st.subheader("Best & Worst Performing Product")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_count", y="product_category_name_english",
            data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Sales", fontsize=30)
ax[0].set_title("Best Performing Product", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(
    by="product_count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Sales", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Customer Demographic
st.subheader("Customer Demographics")

fig, ax = plt.subplots(figsize=(20, 10))
most_common_state = bystate_df.loc[bystate_df['customer_count'].idxmax(
), 'customer_state']
bystate_df = bystate_df.sort_values(by='customer_count', ascending=False)

sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df,
    palette=["#90CAF9" if state == most_common_state else "#D3D3D3" for state in bystate_df['customer_state']])

ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.set_ylabel("State")
ax.set_xlabel("Number of Customers")
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=20)
st.pyplot(fig)

st.caption('Copyright (C) E-Heisenberg Store')
