import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import json
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import yaml
import os

# Load configuration
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "GPU Resource Profiler Dashboard"

# Layout
app.layout = html.Div([
    html.H1("GPU Resource Profiler Dashboard", style={'textAlign': 'center'}),
    
    # Controls
    html.Div([
        html.Div([
            html.Label("Profile File:"),
            dcc.Dropdown(
                id='profile-dropdown',
                options=[],  # Will be populated on load
                value=None
            )
        ], style={'width': '30%', 'display': 'inline-block'}),
        
        html.Div([
            html.Label("Time Range:"),
            dcc.Dropdown(
                id='time-range',
                options=[
                    {'label': 'Last 5 minutes', 'value': '5m'},
                    {'label': 'Last 15 minutes', 'value': '15m'},
                    {'label': 'Last 30 minutes', 'value': '30m'},
                    {'label': 'Last hour', 'value': '1h'},
                    {'label': 'All', 'value': 'all'}
                ],
                value='15m'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginLeft': '20px'})
    ], style={'marginBottom': '20px'}),
    
    # GPU Utilization
    html.Div([
        html.H3("GPU Utilization"),
        dcc.Graph(id='utilization-graph')
    ]),
    
    # Memory Usage
    html.Div([
        html.H3("GPU Memory Usage"),
        dcc.Graph(id='memory-graph')
    ]),
    
    # Temperature
    html.Div([
        html.H3("GPU Temperature"),
        dcc.Graph(id='temperature-graph')
    ]),
    
    # Power Usage
    html.Div([
        html.H3("GPU Power Usage"),
        dcc.Graph(id='power-graph')
    ]),
    
    # Process List
    html.Div([
        html.H3("Active GPU Processes"),
        html.Div(id='process-list')
    ]),
    
    # Auto-refresh interval
    dcc.Interval(
        id='interval-component',
        interval=config['dashboard']['refresh_interval'] * 1000,  # in milliseconds
        n_intervals=0
    )
])

def load_profile_data(profile_file):
    """Load and process profile data from JSON file."""
    with open(profile_file, 'r') as f:
        data = json.load(f)
    
    # Convert to DataFrame
    gpu_stats = []
    for sample in data['gpu_stats']:
        for gpu in sample:
            gpu['timestamp'] = datetime.fromisoformat(gpu['timestamp'])
            gpu_stats.append(gpu)
    
    return pd.DataFrame(gpu_stats)

def update_profile_list():
    """Update the list of available profile files."""
    profile_dir = Path(config['profiling']['output_dir'])
    if not profile_dir.exists():
        return []
    
    profiles = []
    for file in profile_dir.glob('profile_*.json'):
        profiles.append({
            'label': file.name,
            'value': str(file)
        })
    return sorted(profiles, key=lambda x: x['label'], reverse=True)

@app.callback(
    Output('profile-dropdown', 'options'),
    Input('interval-component', 'n_intervals')
)
def update_profile_dropdown(n):
    return update_profile_list()

@app.callback(
    [Output('utilization-graph', 'figure'),
     Output('memory-graph', 'figure'),
     Output('temperature-graph', 'figure'),
     Output('power-graph', 'figure'),
     Output('process-list', 'children')],
    [Input('profile-dropdown', 'value'),
     Input('time-range', 'value'),
     Input('interval-component', 'n_intervals')]
)
def update_graphs(profile_file, time_range, n):
    if not profile_file:
        return {}, {}, {}, {}, "No profile selected"
    
    # Load data
    df = load_profile_data(profile_file)
    
    # Filter by time range
    if time_range != 'all':
        now = df['timestamp'].max()
        if time_range == '5m':
            start_time = now - timedelta(minutes=5)
        elif time_range == '15m':
            start_time = now - timedelta(minutes=15)
        elif time_range == '30m':
            start_time = now - timedelta(minutes=30)
        else:  # 1h
            start_time = now - timedelta(hours=1)
        df = df[df['timestamp'] >= start_time]
    
    # Create figures
    utilization_fig = go.Figure()
    memory_fig = go.Figure()
    temperature_fig = go.Figure()
    power_fig = go.Figure()
    
    # Add traces for each GPU
    for gpu_id in df['device_id'].unique():
        gpu_data = df[df['device_id'] == gpu_id]
        name = gpu_data['name'].iloc[0]
        
        # Utilization
        utilization_fig.add_trace(go.Scatter(
            x=gpu_data['timestamp'],
            y=gpu_data['utilization'],
            name=f"{name} (GPU {gpu_id})",
            mode='lines'
        ))
        
        # Memory
        memory_fig.add_trace(go.Scatter(
            x=gpu_data['timestamp'],
            y=gpu_data['memory_used'],
            name=f"{name} (GPU {gpu_id})",
            mode='lines'
        ))
        
        # Temperature
        temperature_fig.add_trace(go.Scatter(
            x=gpu_data['timestamp'],
            y=gpu_data['temperature'],
            name=f"{name} (GPU {gpu_id})",
            mode='lines'
        ))
        
        # Power
        power_fig.add_trace(go.Scatter(
            x=gpu_data['timestamp'],
            y=gpu_data['power_usage'],
            name=f"{name} (GPU {gpu_id})",
            mode='lines'
        ))
    
    # Update layouts
    for fig in [utilization_fig, memory_fig, temperature_fig, power_fig]:
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Value",
            template="plotly_dark" if config['dashboard']['theme'] == 'dark' else "plotly_white",
            showlegend=True
        )
    
    utilization_fig.update_layout(yaxis_title="Utilization (%)")
    memory_fig.update_layout(yaxis_title="Memory (MB)")
    temperature_fig.update_layout(yaxis_title="Temperature (°C)")
    power_fig.update_layout(yaxis_title="Power (W)")
    
    # Create process list
    latest_data = df[df['timestamp'] == df['timestamp'].max()]
    process_list = []
    
    for _, gpu in latest_data.iterrows():
        process_list.append(html.H4(f"GPU {gpu['device_id']} ({gpu['name']})"))
        if gpu['processes']:
            table = html.Table([
                html.Thead(html.Tr([
                    html.Th("PID"),
                    html.Th("Name"),
                    html.Th("Memory (MB)"),
                    html.Th("User")
                ])),
                html.Tbody([
                    html.Tr([
                        html.Td(proc['pid']),
                        html.Td(proc['name']),
                        html.Td(proc['memory_used']),
                        html.Td(proc['username'])
                    ]) for proc in gpu['processes']
                ])
            ], style={'width': '100%', 'marginBottom': '20px'})
            process_list.append(table)
        else:
            process_list.append(html.P("No active processes"))
    
    return utilization_fig, memory_fig, temperature_fig, power_fig, process_list

def main():
    """Run the dashboard server."""
    app.run(
        host=config['dashboard']['host'],
        port=config['dashboard']['port'],
        debug=True
    )

if __name__ == '__main__':
    main() 