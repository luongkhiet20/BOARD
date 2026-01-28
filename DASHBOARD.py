import streamlit as st
import pandas as pd
import plotly.express as px

# ================= LOAD DATA =================
@st.cache_data
def load_data():
    df = pd.read_excel('SP.xlsx', sheet_name='Trang tính1')
    df['Số lượng đã bán'] = pd.to_numeric(df['Số lượng đã bán'], errors='coerce')
    df['Hoa hồng'] = pd.to_numeric(df['Hoa hồng'], errors='coerce')
    df['Giá'] = pd.to_numeric(df['Giá'], errors='coerce')
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce').fillna(5.0)
    return df

df = load_data()

st.set_page_config(page_title="Product BI Dashboard", layout="wide")
st.title("Dashboard")

# ================= SIDEBAR FILTER =================
st.sidebar.header("Bộ lọc dữ liệu")

shop = st.sidebar.multiselect("Cửa hàng", df['Tên cửa hàng'].unique())
price_range = st.sidebar.slider(
    "Khoảng giá",
    0,
    int(df['Giá'].max()),
    (0, int(df['Giá'].max()))
)

filtered_df = df[
    (df['Tên cửa hàng'].isin(shop) if shop else True) &
    (df['Giá'].between(*price_range))
]

# ================= PAGE SELECT =================
page = st.sidebar.selectbox("Chọn Trang", [
    "Tổng quan điều hành",
    "Phân tích đối thủ",
    "Tiếp thị liên kết"
])

# ================= PAGE 1 =================
if page == "Tổng quan điều hành":

    st.subheader("Tổng quan")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng số lượng đã bán",
                f"{filtered_df['Số lượng đã bán'].sum():,.0f}")

    col2.metric("Tỉ lệ hoa hồng TB (%)",
                f"{filtered_df['Tỉ lệ hoa hồng'].mean():.2f}%")

    col3.metric("Số sản phẩm",
                len(filtered_df))

    col4.metric("Rating trung bình",
                f"{filtered_df['Rating'].mean():.2f}")

    st.subheader("Số lượng bán theo cửa hàng")
    fig_bar = px.bar(
        filtered_df.groupby('Tên cửa hàng')['Số lượng đã bán']
        .sum().reset_index(),
        x='Tên cửa hàng',
        y='Số lượng đã bán'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 5 sản phẩm bán chạy")
        top5 = filtered_df.nlargest(
            5, 'Số lượng đã bán'
        )[['Tên sản phẩm', 'Số lượng đã bán']]
        st.bar_chart(top5.set_index('Tên sản phẩm'))

    with col2:
        st.subheader("Tỷ trọng doanh số theo shop")
        fig_pie = px.pie(
            filtered_df.groupby('Tên cửa hàng')['Số lượng đã bán']
            .sum().reset_index(),
            values='Số lượng đã bán',
            names='Tên cửa hàng'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ================= PAGE 2 =================
elif page == "Phân tích đối thủ":

    st.subheader("So sánh hiệu suất giữa các cửa hàng")

    kpi_df = filtered_df.groupby('Tên cửa hàng').agg({
        'Số lượng đã bán': 'sum',
        'Giá': 'mean',
        'Rating': 'mean'
    }).round(2)

    st.dataframe(kpi_df, use_container_width=True)

    fig_group = px.bar(
        kpi_df.reset_index().melt(id_vars='Tên cửa hàng'),
        x='Tên cửa hàng',
        y='value',
        color='variable',
        barmode='group'
    )
    st.plotly_chart(fig_group, use_container_width=True)

# ================= PAGE 3 =================
# so sánh tỉ lệ hoa hồng cả 3 brand
# ================= PAGE 3 =================
# ================= PAGE 3 =================
elif page == "Tiếp thị liên kết":

    st.subheader("So sánh hiệu quả hoa hồng giữa các cửa hàng")

    # KPI
    col1, col2 = st.columns(2)

    col1.metric("Hoa hồng trung bình / sản phẩm",
                f"{filtered_df['Hoa hồng'].mean():,.0f}")

    col2.metric("Tỉ lệ hoa hồng TB (%)",
                f"{filtered_df['Tỉ lệ hoa hồng'].mean():.2f}%")

    # Bảng tổng hợp theo shop (hoa hồng trung bình)
    commission_df = filtered_df.groupby('Tên cửa hàng').agg({
        'Hoa hồng': 'mean',
        'Tỉ lệ hoa hồng': 'mean',
        'Số lượng đã bán': 'sum',
        'Giá': 'mean'
    }).round(2).reset_index()

    # Đổi tên cột cho rõ nghĩa
    commission_df = commission_df.rename(columns={
        'Hoa hồng': 'Hoa hồng trung bình',
        'Tỉ lệ hoa hồng': 'Tỉ lệ hoa hồng TB (%)',
        'Giá': 'Giá trung bình'
    })

    st.subheader("Bảng hiệu suất hoa hồng theo shop")
    st.dataframe(commission_df, use_container_width=True)

    # Biểu đồ hoa hồng trung bình
    fig_commission = px.bar(
        commission_df,
        x='Tên cửa hàng',
        y='Hoa hồng trung bình',
        title='Hoa hồng trung bình theo cửa hàng'
    )
    st.plotly_chart(fig_commission, use_container_width=True)

    # Biểu đồ tỉ lệ hoa hồng
    fig_rate = px.bar(
        commission_df,
        x='Tên cửa hàng',
        y='Tỉ lệ hoa hồng TB (%)',
        title='Tỉ lệ hoa hồng trung bình (%)'
    )
    st.plotly_chart(fig_rate, use_container_width=True)

