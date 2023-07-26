import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv("./OCEAN_BESE11A.csv")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the header element
header = html.Header(
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Exploratory Data Analysis", href="#")),
            dbc.NavItem(dbc.NavLink("About", href="#")),
        ],
        brand="My Dash App",
        brand_href="#",
        color="primary",
        dark=True,
    )
)

def define_card(column_name, most_caption, least_caption):
    return dbc.Col(dbc.Card(
            dbc.CardBody([
                html.H4(column_name, className=column_name.lower()),
                html.P(f'{most_caption}: {", ".join(df["Name"][df[column_name] == df[column_name].max()].values)}'),
                html.P(f'{least_caption}: {", ".join(df["Name"][df[column_name] == df[column_name].min()].values)}'),
            ]),
        ))

# Define the layout of the app
app.layout = html.Div([
    header,  # Include the header element in the layout
    html.Br(),  # Line break
    html.H2("Quick Insights"),  # Heading for the entire section
    dbc.Row([
        define_card(column_name="Openness", most_caption="Most open", least_caption="Least open"),
        define_card(column_name="Conscientiousness", most_caption="Most organized", least_caption="Most erratic"),      
    ], className="w-100"),
    html.Br(),  # Line break
    # 'Extraversion', 'Agreeableness', 'Neuroticism'
    dbc.Row([
        define_card(column_name="Extraversion", most_caption="Most extroverted", least_caption="Most introverted"),
        define_card(column_name="Agreeableness", most_caption="Most agreeable", least_caption="Least agreeable"),
        define_card(column_name="Neuroticism", most_caption="Most neurotic", least_caption="Least neurotic"),
    ], className="w-100"),
    html.Br(),  # Line break
    html.H2("Radar Charts"),  # Heading for the entire section
    dcc.Dropdown(
        id='name-dropdown',
        options=[{'label': name, 'value': name} for name in df['Name']],
        value=df['Name'][0],  # Default value for the dropdown
        multi=True
    ),
    html.Div(
        dcc.Graph(id='radar-chart'),
        id='radar-chart-container',
        style={'display':'flex', 'justify-content':'center'}
    ),
    html.Br(),  # Line break
    html.H2("Exploratory Data Analysis"),  # Heading for the entire section
    dcc.Graph(id='bar-chart'),
    dcc.Graph(id='correlation-matrix', figure={}),
    dcc.Graph(id='line-chart'),    
])

# Define the callback to update the radar chart based on the selected name
@app.callback(
    Output('radar-chart', 'figure'),
    [
        Input('name-dropdown', 'value'),
    ]
)

def update_radar_chart(selected_name):
    if type(selected_name) == str:
        selected_name = [selected_name]
    
    categories = ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism']

    fig = go.Figure()

    for name in selected_name:
        selected_data = df[df['Name'] == name]

        values = selected_data[categories].values.tolist()[0]

        # Append the first variable at the end to close the loop in the chart
        values.append(values[0])

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=name
        ))

    # Update the layout for better visualization
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
        ),
        showlegend=True,
        height=600,
        width=800
    )

    return fig

# Initialize the figure outside the callback
traits = ["Openness", "Conscientiousness", "Extraversion", "Agreeableness", "Neuroticism"]
genders = df["Gender"].unique()

fig_bar = go.Figure()

# Define the callback to update the bar chart
@app.callback(
    dash.dependencies.Output('bar-chart', 'figure'),
    [dash.dependencies.Input('bar-chart', 'figure')]
)
def update_bar_chart(_):
    fig_bar.data = []  # Clear the existing data before updating
    traits = ['Openness', 'Conscientiousness', 'Extraversion', 'Agreeableness', 'Neuroticism']
    genders = ['M', 'F']

    # for trait in traits:
    for gender in genders:
        avg_value = [df[df['Gender'] == gender][trait].mean() for trait in traits]
        fig_bar.add_trace(go.Bar(
            x=traits,
            y=avg_value,
            name=gender,
        ))

    fig_bar.update_layout(
        barmode='group',
        xaxis_title='Personality Trait',
        yaxis_title='Score',
        title="Measuring Gender Disparity in Personality Traits"
    )

    return fig_bar


# Define the callback to update the correlation matrix heatmap
@app.callback(
    dash.dependencies.Output('correlation-matrix', 'figure'),
    [dash.dependencies.Input('correlation-matrix', 'figure')]
)
def update_correlation_matrix(_):
    fig = go.Figure(data=go.Heatmap(z=df.loc[:, traits].corr().values, x=traits, y=traits, colorscale='Viridis'))
    fig.update_layout(
        title='Correlation Matrix',
        xaxis_title='Personality Traits',
        yaxis_title='Personality Traits',
    )
    return fig


# Define the callback to update the line chart
@app.callback(
    dash.dependencies.Output('line-chart', 'figure'),
    [dash.dependencies.Input('line-chart', 'figure')]
)
def update_line_chart(_):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Neuroticism'],
        y=df['Conscientiousness'],
        mode='markers',
        name='Conscientiousness'
    ))

    fig.update_layout(
        title='Conscientiousness against Neuroticism',
        xaxis_title='Neuroticism',
        yaxis_title='Conscientiousness',
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)