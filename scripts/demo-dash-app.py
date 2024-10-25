import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64

# Initialize the Dash app
app = dash.Dash(__name__)

# Sample data for story analysis
df = pd.DataFrame({
    "Scene": ["Scene 1", "Scene 2", "Scene 3", "Scene 4", "Scene 5"],
    "Tension": [10, 40, 60, 80, 30],
    "Characters": ["A, B", "A, C", "B, C", "A, B", "A, B, C"]
})

# Generate a simple tension curve using Plotly
tension_fig = px.line(df, x="Scene", y="Tension", title="Tension Curve")

# Create a character interaction graph using NetworkX
def generate_character_graph():
    G = nx.Graph()

    # Add nodes (characters) and edges (relationships)
    G.add_edges_from([("Character A", "Character B"),
                      ("Character A", "Character C"),
                      ("Character B", "Character C")])

    # Draw the graph to a plot and convert it to a base64 image for display in Dash
    fig, ax = plt.subplots()
    nx.draw(G, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, ax=ax)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return f"data:image/png;base64,{image_base64}"

# Layout for the Dash app
app.layout = html.Div([
    html.H1("Story Analysis Dashboard"),

    # Display the tension curve graph
    dcc.Graph(
        id='tension-graph',
        figure=tension_fig
    ),

    # Display the character relationship graph as an image
    html.Div([
        html.H2("Character Relationship Graph"),
        html.Img(src=generate_character_graph(), style={'width': '50%'})
    ])
])

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
