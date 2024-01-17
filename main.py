from dash import Dash, html, dcc, Input, Output, Patch, ALL, State
from plotly.subplots import make_subplots
from simulate import simulate
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

prev_store = {
    'ts': None,
    'step': None,
    'v_res': None,
    'error_res': None,
    'int_res': None,
    'sp_res': None,
    'angles_res': None
}
app.layout = dbc.Row([
    dbc.Col([
        html.Aside([
            html.H1(['PI Cruise Control'], className='text-center'),
            dbc.Button('Update Charts', id='update-charts', n_clicks=0, style={'width': '100%', 'margin': '10px 0'}),
            # Variables
            html.H4(['Simulation Variables'], className='mb-1 mt-3'),
            html.Div([
                html.Div([
                    html.P(children=['Time [s]'], className='mb-2'),
                    dbc.Input(id="time", type="number", placeholder="300.0", value=300.0, min=1),
                ]),

                html.Div([
                    html.P(children=['Load [kg]'], className='mb-2'),
                    dbc.Input(id="load", type="number", placeholder="200.0", value=200.0, min=0),
                ]),

                html.Div([
                    html.P(children=['Initial Speed [m/s]'], className='mb-2'),
                    dbc.Input(id="v0", type="number", placeholder="0", value=0, min=0),
                ]),

                html.Div([
                    html.P(children=['Initial pedal [%]'], className='mb-2'),
                    dbc.Input(id="ubias", type="number", placeholder="0", value=0, min=-50, max=100),
                ]),

            ], style={
                'display': 'grid',
                'grid-template-columns': 'repeat(2, 1fr)',
                'gap': '6px',
            }),
            html.H4(['PI Regulation'], className='mb-1 mt-3'),
            html.Div([
                html.Div([
                    html.P(children=['Kc'], className='mb-2'),
                    dbc.Input(id="kc", type="number", placeholder="0", value=0.8),
                ]),

                html.Div([
                    html.P(children=['TauI'], className='mb-2'),
                    dbc.Input(id="taui", type="number", placeholder="0", value=50),
                ]),
            ], style={
                'display': 'grid',
                'grid-template-columns': 'repeat(2, 1fr)',
                'gap': '6px',
            }),
            # Set Points
            html.H4(['Set points'], className='mb-1 mt-3'),
            html.Div([
                dbc.Button('Add Set Point in time', outline=True, size='sm', color='info', id='add-set-point',
                           n_clicks=0, style={
                        'margin-top': '10px',
                        'width': '100%'
                    }),
                html.Div(id="set-point-container", children=[]),
            ]),

            # Angle
            html.H4(['Road Slope'], className='my-1 mt-3'),
            html.Div([
                dbc.Button('Add Angle Change in time', outline=True, size='sm', color='info', id='add-angle',
                           n_clicks=0, style={
                        'margin-top': '10px',
                        'width': '100%'
                    }),
                html.Div(id="angle-container", children=[])
            ])
        ]),
    ], style={
        'max-width': '350px',
        'max-height': '100vh',
        'overflow-y': 'scroll'
    }, className='px-4 py-2 bg-secondary'),

    dbc.Col([
        dcc.Graph(id='vel-graph', style={'height': '100%'}),
    ], style={'max-height': '100vh'}),

], style={'min-height': '100vh'})


@app.callback(
    Output("set-point-container", "children"),
    Input("add-set-point", "n_clicks"),
    State("time", 'value'),
)
def display_set_points(n_clicks, time):
    patched_children = Patch()
    container = html.Div([
        html.Div([
            html.P(children=['Point in Time [s]'], className='mb-2'),
            dbc.Input(type="number", placeholder="0", value=0, max=time,
                      id={"type": "set-point-time", "index": n_clicks}),
        ]),
        html.Div([
            html.P(children=[' velocity [m/s]'], className='mb-2'),
            dbc.Input(type="number", placeholder="20", value=0,
                      id={"type": "set-point-value", "index": n_clicks}),
        ]),
    ], style={
        'display': 'grid',
        'grid-template-columns': 'repeat(2, 1fr)',
        'gap': '4px',
        'padding': '10px',
        'margin': '10px 0'
    })

    patched_children.append(container)
    return patched_children


@app.callback(
    Output("angle-container", "children"),
    Input("add-angle", "n_clicks"),
    State("time", 'value'),
)
def display_angles(n_clicks, time):
    patched_children = Patch()
    container = html.Div([
        html.Div([
            html.P(children=['Point in Time [s]'], className='mb-2'),
            dbc.Input(type="number", placeholder="0", value=0, max=time,
                      id={"type": "angle-time", "index": n_clicks}),
        ]),
        html.Div([
            html.P(children=['Angle°'], className='mb-2'),
            dbc.Input(type="number", placeholder="0", value=0, min=-30, max=30,
                      id={"type": "angle-value", "index": n_clicks}),
        ]),
    ], style={
        'display': 'grid',
        'grid-template-columns': 'repeat(2, 1fr)',
        'gap': '2px',
        'padding': '10px',
        'margin': '10px 0'
    })

    patched_children.append(container)
    return patched_children


@app.callback(
    Output('vel-graph', 'figure'),
    Input('update-charts', 'n_clicks'),
    State('time', 'value'),
    State('load', 'value'),
    State('v0', 'value'),
    State('ubias', 'value'),
    State('kc', 'value'),
    State('taui', 'value'),
    State({'type': 'set-point-time', 'index': ALL}, 'value'),
    State({'type': 'set-point-value', 'index': ALL}, 'value'),
    State({'type': 'angle-time', 'index': ALL}, 'value'),
    State({'type': 'angle-value', 'index': ALL}, 'value'),
)
def display_graph(n_clicks, time, load, v0, ubias, kc, taui, set_point_times, set_point_values, angle_times,
                  angle_values):
    set_points = dict(zip(set_point_times, set_point_values))
    angles = dict(zip(angle_times, angle_values))

    ts, step, v_res, error_res, int_res, sp_res, angles_res = simulate(time, load, v0, ubias, set_points, angles, kc,
                                                                       taui)

    global prev_store

    fig = make_subplots(rows=4, cols=1,
                        subplot_titles=['Velocity and Set Point vs Time', 'Gas Pedal vs Time', 'Error (SP-PV) vs Time',
                                        'Road Slope vs Time'])

    # First subplot
    vel_trace = go.Scatter(x=ts, y=v_res, mode='lines', name='Velocity', line=dict(color='blue', width=3))
    set_point_trace = go.Scatter(x=ts, y=sp_res, mode='lines', name='Set Point',
                                 line=dict(color='black', dash='dash', width=2))
    vel_trace.hovertemplate = '%{x:.2f} s, %{y:.2f} m/s'
    set_point_trace.hovertemplate = '%{x:.2f} s, %{y:.2f} m/s'
    fig.add_trace(vel_trace, row=1, col=1)
    fig.add_trace(set_point_trace, row=1, col=1)

    if prev_store['v_res'] is not None:
        prev_vel_trace = go.Scatter(x=prev_store['ts'], y=prev_store['v_res'], mode='lines',
                                    name='Previous Velocity', line=dict(color='gray', dash='dash', width=2))
        prev_vel_trace.hovertemplate = '%{x:.2f} s, %{y:.2f} m/s'
        fig.add_trace(prev_vel_trace, row=1, col=1)

    # Second subplot
    gas_pedal_trace = go.Scatter(x=ts, y=step, mode='lines', name='Gas Pedal',
                                 line=dict(color='red', dash='dash', width=3))
    gas_pedal_trace.hovertemplate = '%{x:.2f} s, %{y:.2f} %'
    fig.add_trace(gas_pedal_trace, row=2, col=1)
    if prev_store['step'] is not None:
        prev_gas_pedal_trace = go.Scatter(x=prev_store['ts'], y=prev_store['step'], mode='lines',
                                          name='Previous Gas Pedal', line=dict(color='gray', dash='dash', width=2))
        prev_gas_pedal_trace.hovertemplate = '%{x:.2f} s, %{y:.2f} %'
        fig.add_trace(prev_gas_pedal_trace, row=2, col=1)

    # Third subplot
    error_trace = go.Scatter(x=ts, y=error_res, mode='lines', name='Error (SP-PV)', line=dict(color='purple', width=3))
    error_trace.hovertemplate = '%{x:.2f} s, %{y:.2f} m/s'
    fig.add_trace(error_trace, row=3, col=1)
    if prev_store['error_res'] is not None:
        prev_error_trace = go.Scatter(x=prev_store['ts'], y=prev_store['error_res'], mode='lines',
                                      name='Previous Error', line=dict(color='gray', dash='dash', width=2))
        prev_error_trace.hovertemplate = '%{x:.2f} s, %{y:.2f} m/s'
        fig.add_trace(prev_error_trace, row=3, col=1)

    # Forth subplot
    angle_trace = go.Scatter(x=ts, y=angles_res, mode='lines', name='Angle of road',
                             line=dict(color='black', dash='dash', width=3))
    angle_trace.hovertemplate = '%{x:.2f} s, %{y:.2f} degrees'
    fig.add_trace(angle_trace, row=4, col=1)
    if prev_store['angles_res'] is not None:
        prev_angle_trace = go.Scatter(x=prev_store['ts'], y=prev_store['angles_res'], mode='lines',
                                      name='Previous Angle', line=dict(color='gray', dash='dash', width=2))
        angle_trace.hovertemplate = '%{x:.2f} s, %{y:.2f} degrees'
        fig.add_trace(prev_angle_trace, row=4, col=1)

    fig.update_yaxes(title_text='Velocity (m/s)', row=1, col=1)
    fig.update_yaxes(title_text='Gas Pedal (%)', row=2, col=1)
    fig.update_yaxes(title_text='Error (SP-PV)', row=3, col=1)
    fig.update_yaxes(title_text='Angle of road', row=4, col=1)
    fig.update_xaxes(title_text='Time (sec)', row=4, col=1)

    prev_store = {
        'ts': ts,
        'step': step,
        'v_res': v_res,
        'error_res': error_res,
        'int_res': int_res,
        'sp_res': sp_res,
        'angles_res': angles_res
    }

    return fig


if __name__ == '__main__':
    app.run(debug=True)
