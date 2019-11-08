#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import networkx as nx
import plotly.graph_objs as go
import random
from dash.dependencies import Input, Output, State
import time
import datetime
import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css','https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.4.1/semantic.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

dict = {'G':nx.random_geometric_graph(1, 1), 'rate': 0.2, 'recovery':'0.2', 'infected_nodes_info': {}, 'clicks':0}
wait_ies = {'drawing': True}
results = {'s_results': []}

def get_my_graph():
    return dict['G']

def set_my_graph(temp_graph):
    dict['G'] = temp_graph

app.layout = html.Div(className='row', children=[
        html.Div([
        html.Div([
            html.Div([
                html.H1('SIR simulation', style={'color': '#CC6060', 'fontSize': 26}),
                html.Div([
                html.P('Nodos totales', className='my-class', id='n_p'),
                html.Div([
                dcc.Slider(id="nodes_num", min=5, max=50, value=10, step=5, updatemode="drag",
                marks={5: "5", 10: "10", 20: "20", 30: "30", 40: "40", 50: "50"}, className="row"),
                ]),
                ], style={'margin':'30px'}),
                html.Div([
                html.P('Nodos infectados', className='my-class', id='i_p'),
                html.Div([
                dcc.Slider(id="nodes_infected", min=5, max=50, value=5, step=5, updatemode="drag",
                marks={5: "5", 10: "10", 20: "20", 30: "30", 40: "40", 50: "50"}, className="row"),
                ]),
                ],style={'margin':'30px'}),
                html.Div([
                html.P('Radio', className='my-class', id='r_p'),
                html.Div([
                dcc.Slider(id="radius", min=0, max=1, value=0.5, step=0.1,
                marks={0: "0", 0.1:"0.1", 0.2:"0.2", 0.3:"0.3", 0.4:"0.4", 0.5:"0.5", 0.6:"0.6", 0.7:"0.7", 0.8:"0.8", 0.9:"0.9", 1:"1"},
                className="row"),
                html.Div(id='nodes_rad_div'),
                ]),
                ],style={'margin':'30px'}),
                html.Div([
                html.P('Infection rate', className='my-class', id='rate_p'),
                html.Div([
                dcc.Slider(id="rate", min=0, max=1, value=0.5, step=0.1,
                marks={0: "0", 0.1:"0.1", 0.2:"0.2", 0.3:"0.3", 0.4:"0.4", 0.5:"0.5", 0.6:"0.6", 0.7:"0.7", 0.8:"0.8", 0.9:"0.9", 1:"1"},
                className="row"),

                html.Div(id='nodes_rate_div'),
                ]),
                ],style={'margin':'30px'}),
                html.Div([
                html.P('Recovery rate', className='my-class', id='recovery_p'),
                html.Div([
                dcc.Slider(id="recovery", min=0, max=1, value=0.5, step=0.1,
                marks={0: "0", 0.1:"0.1", 0.2:"0.2", 0.3:"0.3", 0.4:"0.4", 0.5:"0.5", 0.6:"0.6", 0.7:"0.7", 0.8:"0.8", 0.9:"0.9", 1:"1"},
                className="row"),

                html.Div(id='nodes_recovery_div'),
                ]),
                ],style={'margin':'30px'}),
                html.Button('Simulate', id='button', className='ui fluid red button'),
            ], className="content", style={'width':'100%'})
        ], className="ui card", style={'width':'100%'}),
        html.Div([
            html.Div([
                html.Div([
                html.P('Results')
                ], className='header'),
                html.P('All results will be shown here.', id='p_results')
            ], className='content')
        ],className='ui card')


        ], className='three columns', style={'margin': '30px', 'fontSize': 14}),
        html.Div([
        # Primer grafo
        dcc.Graph(id="my-graph"),
        dcc.Interval(
            id='interval-component',
            # Current interval
            n_intervals=0,

            # Time in seconds
            interval=10000,
        )
        ], className='eight columns'),
    ])


def update_infected():
    G = dict['G']
    rate = dict['rate']
    print("Updating infected nodes...")
    # Updating infected
    infected_nodes_info = dict['infected_nodes_info'].copy()
    temp_infected_nodes_info = infected_nodes_info.copy()
    # For each node in infected ones
    for node in infected_nodes_info:
        # For each neighbor of an infected node
        for neighbor in G.neighbors(node):
            # If is not infected
            if not neighbor in infected_nodes_info:
                posibility = [True] * int(rate * 10) + [False] * int((1-rate)*10)
                if random.choice(posibility):
                    # Infect
                    temp_infected_nodes_info[neighbor] = True
    # Update infected info
    dict['infected_nodes_info'] = temp_infected_nodes_info
    print("Infected nodes updated")
    return

def recover_infected():
    recovery = dict['recovery']
    # Randomly recovering nodes
    infected_nodes_info = dict['infected_nodes_info'].copy()
    temp_infected_nodes_info = dict['infected_nodes_info'].copy()
    for node in infected_nodes_info:
        posibility = [True] * int(recovery * 10) + [False] * int((1-recovery)*10)
        if random.choice(posibility):
            # Recover node
            temp_infected_nodes_info.pop(node)
    dict['infected_nodes_info'] = temp_infected_nodes_info
    return

def draw_a_graph():
    G = dict['G'].copy()
    infected_nodes_info = dict['infected_nodes_info'].copy()
    print("Drawing graph")
    pos = nx.get_node_attributes(G, 'pos')
    dmin = 1
    ncenter = 0
    for abigail in pos:
        x, y = pos[abigail]
        d = (x - 0.5) ** 2 + (y - 0.5) ** 2
        if d < dmin:
            ncenter = abigail
            dmin = d
    edge_trace = go.Scatter(x=[], y=[], line={'width': 0.5, 'color': '#888'}, hoverinfo='none', mode='lines')
    nodes = G.nodes()
    edges = G.edges()
    for edge in edges:
        x0, y0 = nodes[edge[0]]['pos']
        x1, y1 = nodes[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    node_trace = go.Scatter(x=[], y=[], text=[], mode='markers', hoverinfo='text',
                            marker={'showscale': False, 'colorscale': 'Picnic', 'reversescale': True, 'color': [],
                                    'size': 10,
                                    'colorbar': {'thickness': 10, 'xanchor': 'left',
                                                 'titleside': 'right'},
                                    'line': {'width': 2}})
    nodes = G.nodes()
    to_iterate_arr = range(len(nodes))
    for i in to_iterate_arr:
        x, y = nodes[i]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
    p = nx.single_source_shortest_path_length(G, ncenter)
    adjas = enumerate(G.adjacency())
    for node, adjacencies in adjas:
        color_node = 2
        if node in infected_nodes_info:
            color_node = 0
        node_trace['marker']['color'] += tuple([color_node])
        node_info = 'Is infected: ' + str(node in infected_nodes_info)
        node_trace['text'] += tuple([node_info])
    figure = {"data": [edge_trace, node_trace],
              "layout": go.Layout(showlegend=False, hovermode='closest',
                                  margin={'b': 20, 'l': 5, 'r': 5, 't': 40},
                                  xaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False},
                                  yaxis={'showgrid': False, 'zeroline': False, 'showticklabels': False})}
    print("Graph drawn")
    return figure

@app.callback(
    [
    Output("my-graph", "figure"),
    Output("p_results", "children")
    ],
    [Input('button', 'n_clicks'),
    Input('interval-component', 'n_intervals'),
    ],
    [
    State("nodes_num", "value"),
    State("nodes_infected", "value"),
    State("radius", "value"),
    State("rate","value"),
    State("recovery","value")
    ]
    )


def m_graph(n_clicks, interval_n, nodes_num, nodes_infected, radius, rate, recovery):
    dict['rate']=rate
    dict['recovery']=recovery
    if n_clicks is None or n_clicks > dict['clicks']:
        print("Clicked")
        print("Creating graph")
        dict['clicks']+=1
        dict['infected_nodes_info']={}
        infected_nodes_info = dict['infected_nodes_info']
        infected = 0
        cont = 0

        # Randomly infecting nodes
        while infected < nodes_infected and cont<nodes_num:
            print("Infecting...")
            randy = random.randint(0, nodes_num-1)
            if randy not in infected_nodes_info:
                infected_nodes_info[randy] = True
                infected += 1
            cont += 1

        print("Creating graph with %d nodes and %d as radius. Infecting %d nodes." % (nodes_num, radius, nodes_infected))
        G = nx.random_geometric_graph(nodes_num, radius)
        dict['G'] = G
        print("Trying to draw created")
        figure = draw_a_graph()
        wait_ies['drawing']=False
        return figure, [html.P("Creating graph")]

    infected_nodes_info=dict['infected_nodes_info']
    print("Updating graph")

    G = dict['G']
    rate = dict['rate']

    # Randomly recovering nodes
    recover_infected()

    # Update infected nodes in graph
    update_infected()

    # Print information
    results['s_results']=[html.P('Interval:'),
    html.P(str(interval_n)),
    html.P('Total nodes:'),
    html.P(str(len(G.nodes()))),
    html.P('Number of infected nodes'),
    html.P(str(len(dict['infected_nodes_info'])))
    ]

    print("Interval: ")
    print(interval_n)
    print("Vector de estado de infección:")
    print(infected_nodes_info)
    print("Número de nodos infectados:")
    print(len(dict['infected_nodes_info']))
    print("Número de nodos totales:")
    print(len(G.nodes()))

    dict['G'] = G
    print("Trying to draw")
    figure = draw_a_graph()
    print("Updated graph")
    return figure, results['s_results']

if __name__ == '__main__':
    app.run_server(debug=True)
