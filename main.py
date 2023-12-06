from dash import Dash, html, dcc, Input, Output
from plotly.subplots import make_subplots
from simulate import simulate
import plotly.graph_objects as go

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='vel-graph'),

    html.H4(children=['Time [s]']),
    dcc.Input(id="time", type="number", placeholder="300.0", value=300.0),

    html.H4(children=['Load [kg]']),
    dcc.Input(id="load", type="number", placeholder="200.0", value=200.0),

    html.H4(children=['v0 [m/s]']),
    dcc.Input(id="v0", type="number", placeholder="0", value=0),

    html.H4(children=['ubias [%]']),
    dcc.Input(id="ubias", type="number", placeholder="0", value=0),
])


@app.callback(
    Output('vel-graph', 'figure'),
    Input('time', 'value'),
    Input('load', 'value'),
    Input('v0', 'value'),
    Input('ubias', 'value')
)
def display_graph(time, load, v0, ubias):
    ts, step, v_res, error_res, int_res, sp_res = simulate(time, load, v0, ubias)

    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=['Velocity and Set Point', 'Gas Pedal vs Time', 'Error (SP-PV) vs Time',
                                        'Integral of Error vs Time'])

    # First subplot
    fig.add_trace(go.Scatter(x=ts, y=v_res, mode='lines', name='Velocity', line=dict(color='blue', width=3)),row=1, col=1)
    fig.add_trace(
        go.Scatter(x=ts, y=sp_res, mode='lines', name='Set Point', line=dict(color='black', dash='dash', width=2)),row=1, col=1)
    fig.update_yaxes(title_text='Velocity (m/s)', row=1, col=1)

    # Second subplot
    fig.add_trace(
        go.Scatter(x=ts, y=step, mode='lines', name='Gas Pedal', line=dict(color='red', dash='dash', width=3)),row=1, col=2)
    fig.update_yaxes(title_text='Gas Pedal (%)', row=1, col=2)
    fig.update_xaxes(title_text='Time (sec)', row=1, col=2)

    # Third subplot
    fig.add_trace(go.Scatter(x=ts, y=error_res, mode='lines', name='Error (SP-PV)', line=dict(color='blue', width=3)),row=2, col=1)
    fig.update_yaxes(title_text='Error (SP-PV)', row=2, col=1)
    fig.update_xaxes(title_text='Time (sec)', row=2, col=1)

    # Forth subplot
    fig.add_trace(go.Scatter(x=ts, y=int_res, mode='lines', name='Integral of Error',
                             line=dict(color='black', dash='dash', width=3)),row=2, col=2)
    fig.update_yaxes(title_text='Integral of Error', row=2, col=2)
    fig.update_xaxes(title_text='Time (sec)', row=2, col=2)

    return fig


if __name__ == '__main__':
    app.run(debug=True)
