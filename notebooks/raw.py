# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.17.0",
#     "pandas==2.3.3"
# ]
# ///

import marimo

__generated_with = "0.18.3"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.vstack(
        [
            mo.md("# <center> Raw Data </center>"),
            mo.md(
                "Check [notebooks/data](https://github.com/pranavduraisamy/traffic-accidents-ind/tree/main/notebooks/data) in main branch for complete master data"
            ),
        ]
    )
    return


@app.cell
def _(mo):
    level_options = ["Country", "State"]
    level_radio = mo.ui.radio(options=level_options, value="Country", inline=True)
    return (level_radio,)


@app.cell
def _(level_radio, mo):
    if level_radio.value == "Country":
        df_options = {
            "Cause": "c-causewise.csv",
            "Road": "c-roadwise.csv",
            "Time": "c-timewise.csv",
            "Vehicle": "c-vehiclewise.csv",
        }
    elif level_radio.value == "State":
        df_options = {
            "Fatalities": "s-fatalities.csv",
            "Registered Vehicles": "s-regvehicles.csv",
            "Motorization Rate": "s-motorrate.csv",
            "Fatalities per 1000 vehicles": "s-fatal1000v.csv",
        }
    df_radio = mo.ui.radio(options=df_options, inline=True)
    return df_options, df_radio


@app.cell
def _(df_radio, level_radio, mo):
    mo.hstack(
        [
            mo.vstack([mo.md("### Level: "), level_radio], align="center"),
            mo.vstack([mo.md("### View:"), df_radio], align="center"),
        ],
        align="center",
    )
    return


@app.cell
def _(df_radio, mo, pd):
    df = pd.read_csv(
        "https://raw.githubusercontent.com/pranavduraisamy/traffic-accidents-ind/main/notebooks/data/"
        + df_radio.value
    )
    year_slider = mo.ui.range_slider.from_series(
        df["Year"], show_value=True, debounce=True, label="", full_width=True
    )

    attr_options = df.columns.to_list()
    attr_options.remove("Year")
    attr_select = mo.ui.multiselect(options=attr_options, value=attr_options)
    return attr_select, df, year_slider


@app.cell
def _(attr_select, mo, year_slider):
    mo.hstack(
        [
            mo.vstack([mo.md("### Year: "), year_slider], align="center"),
            mo.vstack([mo.md("### Attributes:"), attr_select], align="center"),
        ],
        align="center",
    )
    return


@app.cell
def _(attr_select, df, df_options, df_radio, level_radio, mo, year_slider):
    start_year = int(year_slider.value[0])
    end_year = int(year_slider.value[1])
    selected_key = list(df_options.keys())[
        list(df_options.values()).index(df_radio.value)
    ]
    filtered_df = (
        df.loc[df["Year"].between(start_year, end_year), ["Year"] + attr_select.value]
        .copy()
        .reset_index(drop=True)
    )
    if level_radio.value == "Country":
        table_title = f"### Nationwide Traffic Fatalities by {selected_key} from {start_year} to {end_year}"
    elif level_radio.value == "State":
        if df_radio.value == "s-regvehicles.csv":
            selected_key += " (in 1000s)"
        table_title = f"### Statewise {selected_key} from {start_year} to {end_year}"
    mo.ui.table(
        data=filtered_df,
        pagination=True,
        label=table_title,
        page_size=25,
        show_column_summaries="chart",
    )
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd

    return mo, pd


if __name__ == "__main__":
    app.run()
