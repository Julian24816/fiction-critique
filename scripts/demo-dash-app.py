# story_analysis_app.py

import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
from dash.dependencies import Input, Output

# Initialize the Dash app
app = dash.Dash(__name__)

# Expanded data with additional relationships and character details
characters = {
    "Character A": {"role": "Protagonist", "description": "The hero of the story."},
    "Character B": {"role": "Mentor", "description": "Guides the protagonist on their journey."},
    "Character C": {"role": "Rival", "description": "A strong competitor with conflicting motives."},
    "Character D": {"role": "Ally", "description": "Supports the protagonist in difficult times."},
    "Character E": {"role": "Antagonist", "description": "The main villain who opposes the protagonist."}
}

relationships = [
    ("Character A", "Character B"),
    ("Character A", "Character C"),
    ("Character A", "Character D"),
    ("Character C", "Character D"),
    ("Character B", "Character D"),
    ("Character A", "Character E"),
    ("Character C", "Character E")
]

# Generate a simple tension curve using Plotly
df = pd.DataFrame({
    "Scene": ["Scene 1", "Scene 2", "Scene 3", "Scene 4", "Scene 5"],
    "Tension": [10, 40, 60, 80, 30]
})
tension_fig = px.line(df, x="Scene", y="Tension", title="Tension Curve")

# Function to create interactive character relationship graph
def generate_interactive_character_graph():
    G = nx.Graph()
    G.add_edges_from(relationships)
    pos = nx.spring_layout(G)
    edge_x = []
    edge_y = []

    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    node_x = []
    node_y = []
    node_text = []
    node_color = []

    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{node}: {characters[node]['role']}")
        node_color.append("blue" if characters[node]["role"] == "Protagonist" else "orange")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(size=20, color=node_color)
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='Interactive Character Relationship Graph',
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    ))

    return fig

# Layout for the Dash app
app.layout = html.Div([
    html.H1("Story Analysis Dashboard"),
    dcc.Graph(id='tension-graph', figure=tension_fig),
    html.Div([
        html.H2("Interactive Character Relationship Graph"),
        dcc.Graph(id='character-relationship-graph', figure=generate_interactive_character_graph())
    ]),
    html.Div([
        html.H2("Character Details"),
        html.Div(id='character-details', children="Click on a character to see details.")
    ])
])

# Callback for displaying character details on click
@app.callback(
    Output('character-details', 'children'),
    Input('character-relationship-graph', 'clickData')
)
def display_character_details(clickData):
    if clickData is None:
        return "Click on a character to see details."
    character_name = clickData['points'][0]['text'].split(":")[0]
    character_info = characters.get(character_name, {})
    return [
        html.H3(f"{character_name}"),
        html.P(f"Role: {character_info['role']}"),
        html.P(f"Description: {character_info['description']}")
    ]

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
