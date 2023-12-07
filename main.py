from dash import Dash, html, dcc, Input, Output, Patch, ALL
from plotly.subplots import make_subplots
from simulate import simulate
import plotly.graph_objects as go

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='vel-graph'),
    html.Div([
        # Variables
        html.Div([
            html.Div([
                html.H4(children=['Time [s]']),
                dcc.Input(id="time", type="number", placeholder="300.0", value=300.0, min=1),
            ]),

            html.Div([
                html.H4(children=['Load [kg]']),
                dcc.Input(id="load", type="number", placeholder="200.0", value=200.0, min=0),
            ]),

            html.Div([
                html.H4(children=['Initial Speed [m/s]']),
                dcc.Input(id="v0", type="number", placeholder="0", value=0, min=0),
            ]),

            html.Div([
                html.H4(children=['Initial pedal position [%]']),
                dcc.Input(id="ubias", type="number", placeholder="0", value=0, min=-50, max=100),
            ]),
        ], style={
            'display': 'grid',
            'grid-template-columns': 'repeat(2, 1fr)',
            'gap': '2px',
            'max-width': '600px',
        }),

        # Set Points
        html.Div([
            html.Button('Add Set Point in time', id='add-set-point', n_clicks=0, style={
                'margin-top': '10px'
            }),
            html.Div(id="set-point-container", children=[], style={
                'max-width': '500px'
            }),
        ]),

        # Angle
        html.Div([
            html.Button('Add Angle Change in time', id='add-angle', n_clicks=0, style={
                'margin-top': '10px'
            }),
            html.Div(id="angle-container", children=[], style={
                'max-width': '500px'
            }),
        ])
    ], style={
        'display': 'grid',
        'grid-template-columns': 'repeat(3, 1fr)',
        'gap': '2px'
    }),

])


@app.callback(
    Output("set-point-container", "children"),
    Input("add-set-point", "n_clicks"),
    Input("time", 'value'),
)
def display_set_points(n_clicks, time):
    patched_children = Patch()
    container = html.Div([
        html.Div([
            html.H4(children=['Point in Time [s]']),
            dcc.Input(type="number", placeholder="0", value=0, max=time,
                      id={"type": "set-point-time", "index": n_clicks}),
        ]),
        html.Div([
            html.H4(children=['Desired velocity [m/s]']),
            dcc.Input(type="number", placeholder="20", value=20,
                      id={"type": "set-point-value", "index": n_clicks}),
        ]),
    ], style={
        'display': 'grid',
        'grid-template-columns': 'repeat(2, 1fr)',
        'gap': '2px',
        'border': '1px black solid',
        'padding': '10px',
        'margin': '10px 0'
    })

    patched_children.append(container)
    return patched_children

@app.callback(
    Output("angle-container", "children"),
    Input("add-angle", "n_clicks"),
    Input("time", 'value'),
)
def display_angles(n_clicks, time):
    patched_children = Patch()
    container = html.Div([
        html.Div([
            html.H4(children=['Point in Time [s]']),
            dcc.Input(type="number", placeholder="0", value=0, max=time,
                      id={"type": "angle-time", "index": n_clicks}),
        ]),
        html.Div([
            html.H4(children=['Angle°']),
            dcc.Input(type="number", placeholder="0", value=0, min=-30, max=30,
                      id={"type": "angle-value", "index": n_clicks}),
        ]),
    ], style={
        'display': 'grid',
        'grid-template-columns': 'repeat(2, 1fr)',
        'gap': '2px',
        'border': '1px black solid',
        'padding': '10px',
        'margin': '10px 0'
    })

    patched_children.append(container)
    return patched_children


@app.callback(
    Output('vel-graph', 'figure'),
    Input('time', 'value'),
    Input('load', 'value'),
    Input('v0', 'value'),
    Input('ubias', 'value'),
    Input({'type': 'set-point-time', 'index': ALL}, 'value'),
    Input({'type': 'set-point-value', 'index': ALL}, 'value'),
    Input({'type': 'angle-time', 'index': ALL}, 'value'),
    Input({'type': 'angle-value', 'index': ALL}, 'value'),
)
def display_graph(time, load, v0, ubias, set_point_times, set_point_values, angle_times, angle_values):
    set_points = dict(zip(set_point_times, set_point_values))
    angles = dict(zip(angle_times, angle_values))

    # Debug logs
    # print('-----------------------')
    # print('set-points')
    # print('times',set_point_times)
    # print('values',set_point_values)
    # print('angles')
    # print('times', angle_times)
    # print('values', angle_values)
    # print('-----------------------')

    ts, step, v_res, error_res, int_res, sp_res, angles_res = simulate(time, load, v0, ubias, set_points, angles)

    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=['Velocity and Set Point vs Time', 'Gas Pedal vs Time', 'Error (SP-PV) vs Time',
                                        'Road Slope vs Time'])

    # First subplot
    fig.add_trace(go.Scatter(x=ts, y=v_res, mode='lines', name='Velocity', line=dict(color='blue', width=3)), row=1,
                  col=1)
    fig.add_trace(
        go.Scatter(x=ts, y=sp_res, mode='lines', name='Set Point', line=dict(color='black', dash='dash', width=2)),
        row=1, col=1)
    fig.update_yaxes(title_text='Velocity (m/s)', row=1, col=1)

    # Second subplot
    fig.add_trace(
        go.Scatter(x=ts, y=step, mode='lines', name='Gas Pedal', line=dict(color='red', dash='dash', width=3)), row=1,
        col=2)
    fig.update_yaxes(title_text='Gas Pedal (%)', row=1, col=2)
    fig.update_xaxes(title_text='Time (sec)', row=1, col=2)

    # Third subplot
    fig.add_trace(go.Scatter(x=ts, y=error_res, mode='lines', name='Error (SP-PV)', line=dict(color='purple', width=3)),
                  row=2, col=1)
    fig.update_yaxes(title_text='Error (SP-PV)', row=2, col=1)
    fig.update_xaxes(title_text='Time (sec)', row=2, col=1)

    # Forth subplot
    fig.add_trace(go.Scatter(x=ts, y=angles_res, mode='lines', name='Angle of road',
                             line=dict(color='black', dash='dash', width=3)), row=2, col=2)
    fig.update_yaxes(title_text='Angle of road', row=2, col=2)
    fig.update_xaxes(title_text='Time (sec)', row=2, col=2)

    return fig


if __name__ == '__main__':
    app.run(debug=True)

