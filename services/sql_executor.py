from db.connection import execute_sql



def run_widget_queries(spec: dict):
    for section in spec["sections"]:
        for widget in section["widgets"]:
            sql = widget["sql"]

            df = execute_sql(sql)

            widget["data"] = df.to_dict(orient="records")

    return spec