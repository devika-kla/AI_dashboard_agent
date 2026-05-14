import requests
import streamlit as st
import plotly.graph_objects as go

API_URL = "http://localhost:8000/generate-dashboard"

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI KPI Dashboard",
    layout="wide",
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.main {
    background-color: #f4f7fb;
}

.block-container {
    padding-top: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    padding-bottom: 3rem;
}

/* HERO */

.hero {
    padding: 1rem 0 2rem 0;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 0.3rem;
}

.hero-subtitle {
    font-size: 1.1rem;
    color: #64748b;
}

/* SECTION TITLE */

.section-title {
    font-size: 2rem;
    font-weight: 800;
    color: #0f172a;
    margin-top: 2rem;
    margin-bottom: 1.5rem;
}

/* KPI CARD */

.kpi-card {
    background: white;
    border-radius: 22px;
    padding: 1.5rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 4px 18px rgba(0,0,0,0.05);
    min-height: 140px;
}

.kpi-title {
    font-size: 1rem;
    color: #64748b;
    margin-bottom: 1rem;
}

.kpi-value {
    font-size: 2.7rem;
    font-weight: 800;
    color: #0f172a;
}

/* CHART CARD */

.chart-header {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 1rem;
}

/* BUTTON */

.stButton > button {
    background: #2563eb;
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.7rem 1.5rem;
    font-size: 1rem;
    font-weight: 600;
}

.stButton > button:hover {
    background: #1d4ed8;
}

/* TEXT AREA */

textarea {
    border-radius: 14px !important;
}

</style>
""", unsafe_allow_html=True)
# =====================================================
# HERO SECTION
# =====================================================

st.markdown("""
<div class="hero">
    <div class="hero-title">
        AI KPI Dashboard
    </div>
    <div class="hero-subtitle">
        Interactive analytics powered by AI + SQL
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# INPUT
# =====================================================

kpi_input = st.text_area(
    "Enter KPIs (comma separated)",
    value="monthly sales, top customers, revenue by country",
    height=120
)

# =====================================================
# GENERATE BUTTON
# =====================================================

if st.button("Generate Dashboard"):

    with st.spinner("Generating dashboard..."):

        kpis = [
            k.strip()
            for k in kpi_input.split(",")
            if k.strip()
        ]

        payload = {
            "kpis": kpis
        }

        response = requests.post(
            API_URL,
            json=payload
        )

        # =========================================
        # ERROR
        # =========================================

        if response.status_code != 200:

            st.error(f"API Error: {response.text}")

        # =========================================
        # SUCCESS
        # =========================================

        else:

            dashboard = response.json()

            sections = dashboard.get("sections", [])

            # =========================================
            # RENDER EACH KPI SECTION
            # =========================================

            for section in sections:

                st.markdown(
                    f"""
                    <div class="section-title">
                        {section['kpi'].title()}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                widgets = section.get("widgets", [])

                # -------------------------------------
                # Separate Metrics & Charts
                # -------------------------------------

                metric_widgets = [
                    w for w in widgets
                    if w["chart_type"] == "metric"
                ]

                chart_widgets = [
                    w for w in widgets
                    if w["chart_type"] != "metric"
                ]

                # =====================================
                # KPI CARDS ROW
                # =====================================

                if metric_widgets:

                    cols_count = min(len(metric_widgets), 4)

                    metric_cols = st.columns(cols_count)

                    for idx, widget in enumerate(metric_widgets):

                        col = metric_cols[idx % cols_count]

                        with col:

                            data = widget.get("data", [])

                            value = "N/A"

                            if data:

                                first_row = data[0]

                                value = list(first_row.values())[-1]
                                
                                # format numbers nicely
                                if isinstance(value, float):
                                    value = f"{value:,.2f}"

                                elif isinstance(value, int):
                                    value = f"{value:,}"

                            st.markdown(
                                f"""
                                <div class="kpi-card">
                                    <div class="kpi-title">
                                        {widget['title']}
                                    </div>
                                    <div class="kpi-value">
                                        {value}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                st.markdown(
                    "<div style='height:20px'></div>",
                    unsafe_allow_html=True
                )

                # =====================================
                # CHART GRID
                # =====================================

                if chart_widgets:

                    for i in range(0, len(chart_widgets), 2):

                        row_widgets = chart_widgets[i:i + 2]

                        cols = st.columns(2)

                        for col_idx, widget in enumerate(row_widgets):

                            with cols[col_idx]:

                                chart_container = st.container(border=True)

                                with chart_container:

                                    st.markdown(
                                        f"""
                                        <div class="chart-header">
                                            {widget['title']}
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

                                    data = widget.get("data", [])

                                    chart_type = widget.get(
                                        "chart_type",
                                        "bar"
                                    )

                                    if not data:

                                        st.info("No data available")
                                        continue

                                    columns = list(data[0].keys())

                                    x_col = columns[0]

                                    y_col = (
                                        columns[1]
                                        if len(columns) > 1
                                        else None
                                    )

                                    fig = go.Figure()

                                    # =================================
                                    # LINE CHART
                                    # =================================

                                    if chart_type == "line":

                                        fig.add_trace(
                                            go.Scatter(
                                                x=[
                                                    row[x_col]
                                                    for row in data
                                                ],
                                                y=[
                                                    row[y_col]
                                                    for row in data
                                                ],
                                                mode="lines+markers",
                                            )
                                        )

                                    # =================================
                                    # BAR CHART
                                    # =================================

                                    elif chart_type == "bar":

                                        fig.add_trace(
                                            go.Bar(
                                                x=[
                                                    row[x_col]
                                                    for row in data
                                                ],
                                                y=[
                                                    row[y_col]
                                                    for row in data
                                                ],
                                            )
                                        )

                                        fig.update_xaxes(
                                            tickangle=-35
                                        )

                                    # =================================
                                    # PIE CHART
                                    # =================================

                                    elif chart_type == "pie":

                                        fig.add_trace(
                                            go.Pie(
                                                labels=[
                                                    row[x_col]
                                                    for row in data
                                                ],
                                                values=[
                                                    row[y_col]
                                                    for row in data
                                                ],
                                                hole=0.45,
                                            )
                                        )

                                    # =================================
                                    # TABLE
                                    # =================================

                                    elif chart_type == "table":

                                        st.dataframe(
                                            data,
                                            use_container_width=True,
                                            height=420
                                        )

                                        continue

                                    # =================================
                                    # FIGURE LAYOUT
                                    # =================================

                                    fig.update_layout(
                                        height=420,
                                        paper_bgcolor="white",
                                        plot_bgcolor="white",
                                        margin=dict(
                                            l=10,
                                            r=10,
                                            t=10,
                                            b=10,
                                        ),
                                        font=dict(
                                            family="Inter",
                                            size=14,
                                            color="#111827"
                                        ),
                                    )

                                    st.plotly_chart(
                                        fig,
                                        use_container_width=True
                                    )
                                    

                st.markdown(
                    "<div style='height:40px'></div>",
                    unsafe_allow_html=True
                )