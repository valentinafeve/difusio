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

dict = {'G':nx.random_geometric_graph(1, 1), 'rate': 0.2, 'infected_nodes_info': {}, 'clicks':0}

def get_my_graph():
    return dict['G']

def set_my_graph(temp_graph):
    dict['G'] = temp_graph

app.layout = html.Div(className='row', children=[
        html.Div([
        html.H1('Virus spread simulation', style={'color': '#333399', 'fontSize': 26}),
        html.P('Nodos totales', className='my-class', id='n_p'),
        html.Div([
            dcc.Slider(id="nodes_num", min=5, max=50, value=30, step=2, updatemode="drag",
                         marks={5: "5", 10: "10", 20: "20", 30: "30", 40: "40", 50: "50"}, className="row"),
            html.Div(id='nodes_num_container')
        ], style={'margin-bottom': '20px', 'fontSize': 14}),
        html.P('Nodos infectados', className='my-class', id='i_p'),
        html.Div([
            dcc.Slider(id="nodes_infected", min=5, max=50, value=10, step=1, updatemode="drag",
                         marks={5: "5", 10: "10", 20: "20", 30: "30", 40: "40", 50: "50"}, className="row"),
            html.Div(id='nodes_num_container_uno')
        ], style={'margin-bottom': '20px', 'fontSize': 14}),
        html.P('Radio', className='my-class', id='r_p'),
        html.Div([
            dcc.Slider(id="radius", min=0, max=1, value=1, step=0.1, className="row"),
            html.Div(id='nodes_num_container_dos')
        ], style={'marginBottom': '20px', 'fontSize': 14}),
        html.Button('Simulate', id='button', className='ui fluid green button'),
        html.Div(id='button_output')
        ], className='three columns', style={'margin': '30px', 'fontSize': 14}),
        html.Div([
        # Primer grafo
        dcc.Graph(id="my-graph"),
        # Segundo grafo
        dcc.Graph(id="my-graph-2"),
        dcc.Interval(
            id='interval-component',
            n_intervals=0,

            # Tiempo en segundos
            interval=5000,
        )
        ], className='eight columns'),
    ])

@app.callback(
    Output("my-graph", "figure"),
    [Input('button', 'n_clicks')],
    [
    State("nodes_num", "value"),
    State("nodes_infected", "value"),
    State("radius", "value"),
    ]
    )


def create_graph(n_clicks, n, nodes_infected, radius):
    if n_clicks is not None:
        if(n_clicks > dict['clicks']):
            print("Clicked")
            dict['clicks']+=1
    dict['infected_nodes_info']={}
    print("Creating graph")
    infected_nodes_info = dict['infected_nodes_info']
    infected = 0
    cont = 0

    while infected < nodes_infected and cont<n:
        print("Infecting...")
        randy = random.randint(0, n-1)
        if randy not in infected_nodes_info:
            infected_nodes_info[randy] = True
            infected += 1
        cont += 1

    print("Creating graph with %d nodes and %d as radius. Infecting %d nodes." % (n, radius, nodes_infected))
    set_my_graph(nx.random_geometric_graph(n, radius))
    G = get_my_graph()
    pos = nx.get_node_attributes(G, 'pos')
    dmin = 1
    ncenter = 0
    for n in pos:
        x, y = pos[n]
        d = (x - 0.5) ** 2 + (y - 0.5) ** 2
        if d < dmin:
            ncenter = n
            dmin = d
    edge_trace = go.Scatter(x=[], y=[], line={'width': 0.5, 'color': '#888'}, hoverinfo='none', mode='lines')
    nodes = G.nodes()
    for edge in G.edges():
        x0, y0 = nodes[edge[0]]['pos']
        x1, y1 = nodes[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    node_trace = go.Scatter(x=[], y=[], text=[], mode='markers', hoverinfo='text',
                            marker={'showscale': True, 'colorscale': 'Picnic', 'reversescale': True, 'color': [],
                                    'size': 10,
                                    'colorbar': {'thickness': 10, 'xanchor': 'left',
                                                 'titleside': 'right'},
                                    'line': {'width': 2}})
    nodes = G.nodes()
    for i in range(len(nodes)):
        x, y = nodes[i]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
    p = nx.single_source_shortest_path_length(G, ncenter)
    for node, adjacencies in enumerate(G.adjacency()):
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
    dict['G'] = G
    print("Graph created")
    return figure


@app.callback(
    Output("my-graph-2", "figure"),
    [Input('interval-component', 'n_intervals')])

def update_graph(n):
    print("Updating graph")
    infected_nodes_info = dict['infected_nodes_info'].copy()
    G = dict['G']
    rate = dict['rate']

    # Updating infected
    temp_infected_nodes_info = infected_nodes_info.copy()
    print(G.nodes())
    for node in infected_nodes_info:
        for neighbor in G.neighbors(node):
            if not neighbor in infected_nodes_info:
                posibility = [True] * int(rate * 10) + [False] * int((1-rate)*10)
                if random.choice(posibility):
                    temp_infected_nodes_info[neighbor] = True

    dict['infected_nodes_info'] = temp_infected_nodes_info
    print("Intervalo: ")
    print(n)
    print("Vector de estado de infección:")
    print(infected_nodes_info)
    print("Número de nodos infectados:")
    print(len(dict['infected_nodes_info']))
    print("Número de nodos totales:")
    print(len(G.nodes()))

    pos = nx.get_node_attributes(G, 'pos')
    dmin = 1
    ncenter = 0
    for n in pos:
        x, y = pos[n]
        d = (x - 0.5) ** 2 + (y - 0.5) ** 2
        if d < dmin:
            ncenter = n
            dmin = d
    edge_trace = go.Scatter(x=[], y=[], line={'width': 0.5, 'color': '#888'}, hoverinfo='none', mode='lines')
    nodes = G.nodes()
    for edge in G.edges():
        x0, y0 = nodes[edge[0]]['pos']
        x1, y1 = nodes[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    node_trace = go.Scatter(x=[], y=[], text=[], mode='markers', hoverinfo='text',
                            marker={'showscale': True, 'colorscale': 'Picnic', 'reversescale': True, 'color': [],
                                    'size': 10,
                                    'colorbar': {'thickness': 10, 'xanchor': 'left',
                                                 'titleside': 'right'},
                                    'line': {'width': 2}})
    nodes = G.nodes()
    for i in range(len(nodes)):
        x, y = nodes[i]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
    p = nx.single_source_shortest_path_length(G, ncenter)
    for node, adjacencies in enumerate(G.adjacency()):
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
    dict['G'] = G
    print("Updated graph")
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
