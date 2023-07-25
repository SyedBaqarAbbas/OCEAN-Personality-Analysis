import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv("./OCEAN_BESE11A.csv")

app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.Dropdown(
        id='name-dropdown',
        options=[{'label': name, 'value': name} for name in df['Name']],
        value=df['Name'][0],  # Default value for the dropdown
    ),
    dcc.Graph(id='radar-chart'),
])

# Define the callback to update the radar chart based on the selected name
@app.callback(
    Output('radar-chart', 'figure'),
    [Input('name-dropdown', 'value')]
)
def update_radar_chart(selected_name):
    selected_data = df[df['Name'] == selected_name]
    categories = ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism']
    values = selected_data[categories].values.tolist()[0]

    # Append the first variable at the end to close the loop in the chart
    values.append(values[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill='toself',
    ))

    # Update the layout for better visualization
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
        ),
        showlegend=False
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)