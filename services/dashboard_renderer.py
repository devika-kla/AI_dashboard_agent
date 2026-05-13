import streamlit as st
import pandas as pd
import plotly.express as px



def render_dashboard(spec: dict):
    st.title(spec["dashboard_title"])

    for section in spec["sections"]:
        st.markdown("---")
        st.header(section["kpi"].title())

        cols = st.columns(2)

        widget_index = 0

        for widget in section["widgets"]:
            with cols[widget_index % 2]:
                render_widget(widget)

            widget_index += 1



def render_widget(widget: dict):
    st.subheader(widget["title"])

    df = pd.DataFrame(widget["data"])

    if df.empty:
        st.warning("No data available")
        return

    chart_type = widget["chart_type"]

    if chart_type == "metric":
        value = df.iloc[0, 0]
        st.metric(widget["title"], value)
        return

    if chart_type == "table":
        st.dataframe(df, use_container_width=True)
        return

    columns = df.columns.tolist()

    if len(columns) < 2:
        st.dataframe(df)
        return

    x_col = columns[0]
    y_col = columns[1]

    if chart_type == "line":
        fig = px.line(df, x=x_col, y=y_col)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "bar":
        fig = px.bar(df, x=x_col, y=y_col)
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "pie":
        fig = px.pie(df, names=x_col, values=y_col)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.dataframe(df, use_container_width=True)