import requests
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import dash

# Wetterlage Code
def translate_weathercode(code):
    mapping = {
        0: "Klarer Himmel",
        1: "Überwiegend klar",
        2: "Teilweise bewölkt",
        3: "Bewölkt",
        45: "Nebel",
        48: "Nebel mit Reif",
        51: "Leichter Nieselregen",
        53: "Mäßiger Nieselregen",
        55: "Starker Nieselregen",
        61: "Leichter Regen",
        63: "Mäßiger Regen",
        65: "Starker Regen",
        71: "Leichter Schneefall",
        73: "Mäßiger Schneefall",
        75: "Starker Schneefall",
        80: "Leichter Regenschauer",
        81: "Mäßiger Regenschauer",
        82: "Heftiger Regenschauer",
        95: "Gewitter",
        96: "Gewitter mit leichtem Hagel",
        99: "Gewitter mit starkem Hagel"
    }
    return mapping.get(code, "Unbekannt")


# Map Icons
def weather_icon(code):
    icons = {
        0: "KlarerHimmel.png",
        1: "ÜberwiegendKlar.png",
        2: "TeilweiseBewölkt.png",
        3: "Bewölkt.png",
        45: "Nebel.png",
        48: "NebelMitReif.png",
        51: "LeichterNieselregen.png",
        53: "MäßigerNieselregen.png",
        55: "StarkerNieselregen.png",
        61: "LeichterRegen.png",
        63: "MäßigerRegen.png",
        65: "StarkerRegen.png",
        71: "LeichterSchneefall.png",
        73: "MäßigerSchneefall.png",
        75: "StarkerSchneefall.png",
        80: "LeichterRegenschauer.png",
        81: "MäßigerRegenschauer.png",
        82: "HeftigerRegenschauer.png",
        95: "Gewitter.png",
        96: "GewitterMitLeichtemHagel.png",
        99: "GewitterMitStarkemHagel.png"
    }
    return icons.get(code, "Unbekannt")


def temperature_icon(temp):
    if temp < 5:
        return "cold_temp.png"
    elif temp < 20:
        return "mild_temp.png"
    else:
        return "hot_temp.png"
    

def wind_speed_icon(speed):
    if speed < 10:
        return "low_wind.png"
    elif speed < 20:
        return "mild_wind.png"
    elif speed < 35:
        return "strong_wind.png"
    else:
        return "very_strong_wind.png"


# Stadtsuche
def geocode_city(city_name):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name,
        "countrycodes": "de",
        "format": "json",
        "limit": 1
    }
    headers = {"User-Agent": "WeatherDashboardStudentProject/1.0"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=5)
        data = r.json()
    except:
        return None, "Error"

    if not data:
        return None, "Stadt ungültig"

    try:
        lat = float(data[0]["lat"])
        lon = float(data[0]["lon"])
        return (lat, lon), None
    except:
        return None, "Error"


# Get Weather
def fetch_weather(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&current_weather=true"
        "&hourly=temperature_2m,precipitation,cloudcover,windspeed_10m"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=Europe%2FBerlin"
    )
    return requests.get(url).json()





# Dashboard
app = Dash(__name__)

app.layout = html.Div([

    html.H1("Wetterdashboard Deutschland", style={"textAlign": "center"}),

    # Suchfeld
    html.Div([
        html.Div("Stadt eingeben", style={
            "fontSize": "20px",
            "fontWeight": "500",
            "marginBottom": "8px",
            "textAlign": "center"
        }),

        dcc.Input(
            id="city-input",
            type="text",
            placeholder="z. B. Berlin, Hamburg, München …",
            debounce=True,
            style={
                "width": "360px",
                "padding": "10px",
                "fontSize": "18px",
                "borderRadius": "6px",
                "border": "1px solid #ccc",
                "textAlign": "center"
            }
        )
    ],
    style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "marginBottom": "30px"
    }),

    # Stadtanzeige
    html.Div(
        id="selected-city-display",
        style={
            "textAlign": "center",
            "fontSize": "22px",
            "marginBottom": "20px",
            "fontWeight": "500"
        }
    ),

    html.Div(id="status-message", style={
        "textAlign": "center",
        "color": "red",
        "fontSize": "18px",
        "marginBottom": "15px"
    }),

    # Wetterkarten
    html.Div(id="current-weather", style={
        "display": "flex",
        "justifyContent": "center",
        "gap": "25px",
        "marginBottom": "25px"
    }),

    # Diagramme
    html.Div([
        dcc.Graph(id="temp-hourly", style={"width": "48%", "display": "inline-block"}),
        dcc.Graph(id="precip-hourly", style={"width": "48%", "display": "inline-block"})
    ],
    style={"display": "flex", "justifyContent": "space-between"}),

    html.Div([dcc.Graph(id="daily-forecast")], style={"marginTop": "25px"})
])


# Callback
@app.callback(
    Output("status-message", "children"),
    Output("selected-city-display", "children"),
    Output("current-weather", "children"),
    Output("temp-hourly", "figure"),
    Output("precip-hourly", "figure"),
    Output("daily-forecast", "figure"),
    Input("city-input", "value")
)
def update_dashboard(city_name):

    if not city_name:
        raise dash.exceptions.PreventUpdate

    coords, error = geocode_city(city_name)
    if error:
        return error, "", html.Div(), {}, {}, {}

    lat, lon = coords
    data = fetch_weather(lat, lon)

    # Stadt anzeigen
    city_label = f"Wetterdaten für: {city_name.capitalize()}"

    cw = data["current_weather"]
    weather_desc = translate_weathercode(cw["weathercode"])

    icon_file = weather_icon(cw["weathercode"])
    temp_file = temperature_icon(cw["temperature"])
    wind_file = wind_speed_icon(cw["windspeed"])


    cards = html.Div([
        html.Div([
            html.H3("Temperatur"),
            html.Img(src=f"/assets/{temp_file}", style={"width": "60px", "marginBottom": "10px"}),
            html.P(f"{cw['temperature']} °C")
        ], className="card"),

        html.Div([
            html.H3("Windgeschwindigkeit"),
            html.Img(src=f"/assets/{wind_file}", style={"width": "60px", "marginBottom": "10px"}),
            html.P(f"{cw['windspeed']} km/h")
        ], className="card"),

        html.Div([
            html.H3("Wetterlage"),
            html.Img(src=f"/assets/{icon_file}", style={"width": "60px", "marginBottom": "10px"}),
            html.P(weather_desc)
        ], className="card")
    ],
    style={"display": "flex", "gap": "30px"})

    # Stündlich
    hourly = pd.DataFrame(data["hourly"])
    hourly["time"] = pd.to_datetime(hourly["time"])

    today = pd.Timestamp.now(tz="Europe/Berlin").normalize()
    today_data = hourly[hourly["time"].dt.date == today.date()]

    temp_fig = px.line(
        hourly,
        x="time",
        y="temperature_2m",
        title="Temperaturverlauf (stündlich)",
        labels={"time": "Zeit", "temperature_2m": "Temperatur (°C)"},
        custom_data=["time"]
    )

    temp_fig.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]|%a %d.%m. %H:%M}</b><br>"
        "Temperatur: <b>%{y:.1f} °C</b>"
        "<extra></extra>"
    )
)

    temp_fig.update_layout(
        title="Temperaturverlauf (stündlich)",
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                buttons=[
                    dict(
                        label="Heute",
                        method="update",
                        args=[
                            {"x": [today_data["time"]], "y": [today_data["temperature_2m"]]},
                            {
                                "title": "Temperaturverlauf - Heute",
                                "xaxis.tickformat": "%H:%M",
                                "xaxis.range": [today_data["time"].min(), today_data["time"].max()]
                            }
                        ]
                    ),
                    dict(
                        label="7 Tage",
                        method="update",
                        args=[
                            {"x": [hourly["time"]], "y": [hourly["temperature_2m"]]},
                            {
                                "title": "Temperaturverlauf - Nächste 7 Tage",
                                "xaxis.tickformat": "%a %d.%m.",
                                "xaxis.range": [hourly["time"].min(), hourly["time"].max()]
                            }
                        ]
                    ),
                    
                ],
                pad={"r": 10, "t": 10},
                showactive=True,
                x=1.02,
                xanchor="left",
                y=1.18,
                yanchor="top",
                bgcolor="white",
                bordercolor="#888",
                borderwidth=1,
                font=dict(size=13)
            )
        ],
        xaxis=dict(tickformat="%a %d.%m.")
    )

    precip_fig = px.bar(
        hourly,
        x="time",
        y="precipitation",
        title="Niederschlag (stündlich)",
        labels={"time": "Zeit", "precipitation": "Niederschlag (mm)"}
    )

    # Daily
    daily = pd.DataFrame(data["daily"])

    daily_fig = px.bar(
        daily,
        x="time",
        y="precipitation_sum",
        title="Min / Max Temperatur & Niederschlag je Tag",
        labels={"time": "Datum", "precipitation_sum": "Niederschlag (mm)"}
    )

    daily_fig.add_scatter(
        x=daily["time"],
        y=daily["temperature_2m_max"],
        mode="lines+markers",
        name="Tageshöchsttemperatur"
    )

    daily_fig.add_scatter(
        x=daily["time"],
        y=daily["temperature_2m_min"],
        mode="lines+markers",
        name="Tagestiefsttemperatur"
    )

    return "", city_label, cards, temp_fig, precip_fig, daily_fig


# Start
if __name__ == "__main__":
    app.run(debug=True)