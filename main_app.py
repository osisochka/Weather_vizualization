import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import requests
from dash.exceptions import PreventUpdate

# Настройки API
API_KEY = "a92e99aa09fde9b14642dd11c894bc8c"
BASE_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"
GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"


# Функция для получения координат города
def get_coordinates(city):
    try:
        params = {'q': city, 'appid': API_KEY}
        response = requests.get(GEOCODE_URL, params=params, timeout=5)
        response.raise_for_status()
        geo_data = response.json()
        if geo_data:
            return geo_data[0]['lat'], geo_data[0]['lon']
        else:
            return None, None
    except Exception as e:
        return None, None


# Функция для получения данных о погоде
def get_weather_data(city):
    try:
        params = {'q': city, 'appid': API_KEY, 'units': 'metric'}
        response = requests.get(BASE_URL_FORECAST, params=params, timeout=5)
        response.raise_for_status()
        return response.json().get('list', [])
    except Exception as e:
        return []


# Инициализация Dash приложения
app = dash.Dash(__name__)
app.title = "Маршрутный прогноз погоды"

# Основной макет приложения
app.layout = html.Div([
    html.H1("Прогноз погоды для маршрута", style={'color': '#ffffff', 'textAlign': 'center', 'marginBottom': '20px'}),

    # Блок ввода маршрута
    html.Div([
        html.Label("Введите начальную и конечную точки маршрута:", style={'color': '#ffffff', 'fontSize': '18px'}),
        html.Div([
            dcc.Input(id='start-point', type='text', placeholder="Начальная точка",
                      style={'marginRight': '10px', 'width': '250px', 'padding': '8px'}),
            dcc.Input(id='end-point', type='text', placeholder="Конечная точка", style={'marginRight': '10px', 'width': '250px', 'padding': '8px'}),
        ]),
        html.Button('Добавить промежуточную точку', id='add-stop-btn', n_clicks=0,
                    style={'marginTop': '10px', 'backgroundColor': '#007BFF', 'color': 'white', 'border': 'none',
                           'padding': '10px 20px', 'borderRadius': '5px', 'cursor': 'pointer'}),
        html.Div(id='intermediate-stops', children=[], style={'marginTop': '10px'}),
    ], style={'marginBottom': '20px'}),

    # Параметры прогноза
    html.Div([
        html.Label("Выберите параметры прогноза:", style={'fontWeight': 'bold', 'color': '#ffffff'}),
        dcc.Dropdown(
            id='parameter-dropdown',
            options=[
                {'label': 'Температура', 'value': 'temp'},
                {'label': 'Скорость ветра', 'value': 'wind'},
                {'label': 'Осадки', 'value': 'rain'}
            ],
            value=['temp'],  # Значение по умолчанию
            multi=True,
            style={'width': '100%', 'padding': '8px'}
        ),
        html.Label("Выберите временной интервал прогноза:", style={'marginTop': '10px', 'fontWeight': 'bold', 'color': '#ffffff'}),
        dcc.RadioItems(
            id='interval-selector',
            options=[
                {'label': '1 день', 'value': 1},
                {'label': '3 дня', 'value': 3},
                {'label': '5 дней', 'value': 5}
            ],
            value=1,
            inline=True,
            style={'color': '#ffffff'}
        )
    ], style={'marginBottom': '20px'}),

    # Кнопка получения прогноза
    html.Button('Получить прогноз', id='submit-btn', n_clicks=0,
                style={'backgroundColor': '#007BFF', 'color': 'white', 'border': 'none', 'padding': '10px 20px',
                       'borderRadius': '5px', 'cursor': 'pointer', 'fontSize': '16px'}),

    # Колесо загрузки
    dcc.Loading(id="loading", type="circle", children=[
        html.Div([
            html.H3("Маршрут на карте", style={'marginTop': '30px', 'color': '#FFFFFF'}),
            dcc.Graph(id='map-graph', style={'height': '500px'})
        ])
    ], color='#FFFFFF'),

    # Вывод графиков прогноза
    html.Div(id='weather-output', style={'marginTop': '20px'}),



    # Блок сообщений об ошибках
    html.Div(id='error-message', style={'color': 'red', 'marginTop': '20px'})
], style={
    'background': 'linear-gradient(to right, #7fc7ff, #0077ff)',  # Голубой градиент фона
    'padding': '120px',  # Отступы от краёв страницы
    'minHeight': '100vh',  # Минимальная высота страницы
    'fontFamily': 'Arial, sans-serif'
})


# Callback для добавления промежуточных точек
@app.callback(
    Output('intermediate-stops', 'children'),
    [Input('add-stop-btn', 'n_clicks')],
    [State('intermediate-stops', 'children')]
)
def add_intermediate_stop(n_clicks, children):
    if n_clicks > 0:
        new_input = dcc.Input(
            type='text',
            placeholder=f"Промежуточная точка {len(children) + 1}",
            id={'type': 'stop', 'index': len(children)},
            style={'marginRight': '10px', 'marginTop': '5px', 'padding': '8px'}
        )
        children.append(new_input)
    return children


# Callback для обновления карты и графиков
@app.callback(
    [Output('map-graph', 'figure'),
     Output('weather-output', 'children'),
     Output('error-message', 'children')],
    [Input('submit-btn', 'n_clicks')],
    [State('start-point', 'value'),
     State('end-point', 'value'),
     State('intermediate-stops', 'children'),
     State('parameter-dropdown', 'value'),
     State('interval-selector', 'value')]
)
def update_map_and_weather(n_clicks, start, end, stops, parameters, interval):
    if n_clicks == 0:
        raise PreventUpdate

    if not start or not end:
        return go.Figure(), [], "Ошибка: Укажите начальную и конечную точки маршрута."

    # Собираем маршрут
    route = [start] + [child['props']['value'] for child in stops if child['props']['value']] + [end]
    map_markers = []
    weather_data = {}
    latitudes = []
    longitudes = []
    cities_display = []
    weather_info = {}

    # Получение данных для маршрута
    for city in route:
        lat, lon = get_coordinates(city)
        if lat is None or lon is None:
            return go.Figure(), [], f"Ошибка: Невозможно получить данные для города {city}."
        forecasts = get_weather_data(city)[:8 * interval]
        if not forecasts:
            return go.Figure(), [], f"Ошибка: Нет данных для города {city}."
        weather_data[city] = forecasts
        latitudes.append(lat)
        longitudes.append(lon)
        cities_display.append(city)

        # Сохранение погодных данных для всплывающих подсказок
        weather_info[city] = {
            'temp': forecasts[0]['main']['temp'],
            'wind': forecasts[0]['wind']['speed'],
            'rain': forecasts[0].get('rain', {}).get('3h', 0)
        }

    # Создаём карту
    map_fig = go.Figure()


    # Добавляем маршрут на карту
    map_fig.add_trace(go.Scattermapbox(
        lat=latitudes,
        lon=longitudes,
        mode='markers+lines',
        marker=go.scattermapbox.Marker(size=14),
        text=cities_display,
        hoverinfo='text'
    ))


    # Добавляем погодные условия для каждой точки на карту
    for i, city in enumerate(route):
        info = weather_info.get(city, {})
        text = f"{city}<br>Температура: {info.get('temp', 'N/A')}°C<br>Ветер: {info.get('wind', 'N/A')} м/с<br>Осадки: {info.get('rain', 'N/A')} мм"
        map_fig.add_trace(go.Scattermapbox(
            lat=[latitudes[i]],
            lon=[longitudes[i]],
            mode='markers',
            marker=go.scattermapbox.Marker(size=12, color='red'),
            text=text,
            hoverinfo='text'
        ))

    map_fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=5,
        mapbox_center={"lat": latitudes[0], "lon": longitudes[0]},
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    # Создаём графики
    graphs = []
    for city, forecasts in weather_data.items():
        traces = []
        for param in parameters:
            if param == 'temp':
                y_values = [f['main']['temp'] for f in forecasts]
            elif param == 'wind':
                y_values = [f['wind']['speed'] for f in forecasts]
            elif param == 'rain':
                y_values = [f.get('rain', {}).get('3h', 0) for f in forecasts]
            times = [f['dt_txt'] for f in forecasts]
            traces.append(go.Scatter(x=times, y=y_values, mode='lines+markers', name=param.capitalize(),
                                     hoverinfo='x+y+text', text=[f'{param.capitalize()} = {val}' for val in y_values]))

        graphs.append(dcc.Graph(figure={'data': traces, 'layout': {'title': f'Прогноз для {city}',
                                                                  'xaxis': {'title': 'Время'},
                                                                  'yaxis': {'title': 'Значение'},
                                                                  'hovermode': 'closest'}}))

    return map_fig, graphs, ""


if __name__ == '__main__':
    app.run_server(debug=False)