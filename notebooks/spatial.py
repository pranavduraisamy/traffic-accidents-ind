# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "holoviews==1.22.1",
#     "pandas==2.3.3",
# ]
# ///

import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full", layout_file="layouts/spatial.grid.json")


@app.cell
def _(mo):
    mo.md("""
    # <center> Spatial View </center>
    """)
    return


@app.cell
def _(mo):
    df_options1 = {
        "Fatalities": "s-fatalities.csv",
        "Registered Vehicles": "s-regvehicles.csv",
        "Motorization Rate": "s-motorrate.csv",
        "Fatalities per 1000 vehicles": "s-fatal1000v.csv",
    }
    df_radio1 = mo.ui.radio(options=df_options1, inline=False)

    autoplay_switch = mo.ui.switch(label='### Autoplay')
    compare_switch = mo.ui.switch(label='### Compare')

    get_year, set_year = mo.state(2001)

    mo.hstack([autoplay_switch,compare_switch],justify="space-around")
    return (
        autoplay_switch,
        compare_switch,
        df_options1,
        df_radio1,
        get_year,
        set_year,
    )


@app.cell
def _(compare_switch, df_options1, df_radio1, mo):
    if compare_switch.value:
        df_options2 = dict(filter(lambda i: i[1] != df_radio1.value, df_options1.items()))
        df_radio2 = mo.ui.radio(options=df_options2, inline=False)
        df_stack=mo.hstack([mo.vstack([mo.md('### View A:'), df_radio1]),mo.vstack([mo.md('### View B:'), df_radio2])],justify="space-around")
    else:
        df_stack=mo.vstack([mo.md('### View:'), df_radio1])

    df_stack
    return (df_radio2,)


@app.cell
def _(json):
    with open("https://raw.githubusercontent.com/pranavduraisamy/traffic-accidents-ind/refs/heads/main/notebooks/map/india.geojson") as f:
        geo=json.load(f)
    return (geo,)


@app.cell
def _(df_radio1, pd):
    df1=pd.read_csv("https://raw.githubusercontent.com/pranavduraisamy/traffic-accidents-ind/refs/heads/main/notebooks/data/"+df_radio1.value)
    return (df1,)


@app.cell
def _(get_year, mo, set_year):
    year_slider= mo.ui.slider(start=2001,stop=2022,step=1,full_width=True,value=get_year(), on_change=set_year, debounce=True, label="### Year")
    year_slider
    return


@app.cell
def _(get_year, mo, set_year):
    year_number=mo.ui.number(start=2001,
        stop=2022,
        step=1,
        debounce=True, value=get_year(), on_change=set_year)
    year_number
    return


@app.cell
def _(autoplay_switch, mo):
    if autoplay_switch.value:
        timer = mo.ui.refresh([3,5,7,10,15,20], default_interval=7, label='Refresh in')
    else:
        timer = None
    timer
    return (timer,)


@app.cell
def _(autoplay_switch, get_year, set_year, timer):
    if timer is not None and autoplay_switch.value:
        next_year = get_year() + 1
        if next_year > 2022:
            next_year = 2001
        set_year(next_year)
    return


@app.cell
def _(
    compare_switch,
    df1,
    df_radio1,
    df_radio2,
    geo,
    get_year,
    mo,
    pd,
    plot_basic,
):
    if compare_switch.value:
        df2=pd.read_csv("https://raw.githubusercontent.com/pranavduraisamy/traffic-accidents-ind/refs/heads/main/notebooks/data/"+df_radio2.value)
        plot_stack=mo.hstack([plot_basic(df=df1,geo=geo,df_radio_value=df_radio1.value,year_value=get_year(),compare_value=True),plot_basic(df=df2,geo=geo,df_radio_value=df_radio2.value,year_value=get_year(),compare_value=True)],justify='space-around')

    else:
        plot_stack=plot_basic(df=df1,geo=geo,df_radio_value=df_radio1.value,year_value=get_year(),compare_value=False)

    plot_stack
    return


@app.cell
def _(df_radio1, hv, mo):
    def plot_basic(df,geo,df_radio_value,year_value,compare_value):
        radio_dict = {
        "Fatalities": "s-fatalities.csv",
        "Registered Vehicles": "s-regvehicles.csv",
        "Motorization Rate": "s-motorrate.csv",
        "Fatalities per 1000 vehicles": "s-fatal1000v.csv",
        }
        param_name = [i for i,j in radio_dict.items() if j==df_radio_value]

        polygons=[]
        df_year=df[df.Year==year_value].copy()
        df_year = df_year.drop(columns="Year")
        df_year = df_year.T.reset_index()
        df_year.columns=['state','parameter']

        for feature in geo["features"]:
            geom = feature["geometry"]
            props = feature["properties"]
            props.update({'parameter':df_year[df_year.state==props.get('state')].parameter.values[0]})
            if geom["type"] == "Polygon":
                for poly in geom["coordinates"]:
                    polygons.append({
                        "x": [coords[0] for coords in poly],
                        "y": [coords[1] for coords in poly],
                        **props
                    })
            elif geom["type"] == "MultiPolygon":
                for part in geom["coordinates"]:
                    for poly in part:
                        polygons.append({
                            "x": [coords[0] for coords in poly],
                            "y": [coords[1] for coords in poly],
                            **props
                        })

        if compare_value:
            text_font_size = '40pt'
            frame_width=340
        else:
            text_font_size='52pt'
            frame_width=500

        map_plot = hv.Polygons(polygons,['x', 'y'],[('state', 'State'),('parameter',param_name[0])])
        map_plot.opts(data_aspect=1,frame_width=frame_width, xaxis=False, yaxis=False,show_grid=False,line_color='dimgrey',show_frame=False,colorbar=True,toolbar='above',tools=["hover"], color=hv.dim(param_name[0]),cmap='RdYlGn_r',clabel=param_name[0],title='Distribution of '+param_name[0]+' across states')

        text_plot = hv.Text(92, 36,str(int(year_value))).opts(text_font_size=text_font_size, text_color='lightgray')

        combined_plot = map_plot*text_plot

        return combined_plot

    def plot_compare(df1,geo,df_radio_value1,year_value,compare_value,df2=None,df_radio_value2=None):
        if compare_value:
            plot_stack=mo.hstack([plot_basic(df=df1,geo=geo,df_radio_value=df_radio_value1,year_value=year_value,compare_value=True),plot_basic(df=df2,geo=geo,df_radio_value=df_radio_value2,year_value=year_value,compare_value=True)],justify='space-around')
        else:
           plot_stack=plot_basic(df=df1,geo=geo,df_radio_value=df_radio1.value,year_value=year_value,compare_value=True)
        return plot_stack
    return (plot_basic,)


@app.cell
def _():
    import marimo as mo
    import json
    import holoviews as hv
    import pandas as pd
    import time
    hv.extension('bokeh')
    return hv, json, mo, pd


if __name__ == "__main__":
    app.run()
