import dash
from dash import dcc, html
from dash import ctx as dash_ctx
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import random
from faker import Faker
import time
import threading
import numpy as np

app = dash.Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css'])
server = app.server
app.title = "Ad-Libs"

current_theme = 'dark'
fake = Faker()

ad_types = ["Search", "Display", "Video", "Social Media", "Email"]
regions = ["United States", "Canada", "United Kingdom", "France", "Germany", "Spain", "Italy", "China", "Japan", "India", "Australia", "Brazil", "South Africa", "Russia", "Mexico"]
devices = ["Mobile", "Desktop", "Tablet"]
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
periods = ["Morning", "Afternoon", "Evening", "Night"]

ad_data = []
previous_kpis = {
    'rpc': 0,
    'ctr': 0,
    'cpc': 0,
    'cpa': 0
}

def format_kpi_value(current, previous, prefix='', suffix=''):
    global current_theme
    
    try:
        if isinstance(current, str):
            if '$' in current:
                current = float(current.replace('$', ''))
            elif '%' in current:
                current = float(current.replace('%', ''))
        else:
            current = float(current)
    except ValueError:
        current = 0.0
        
    try:
        if isinstance(previous, str):
            if '$' in previous:
                previous = float(previous.replace('$', ''))
            elif '%' in previous:
                previous = float(previous.replace('%', ''))
        else:
            previous = float(previous) if previous else 0
    except ValueError:
        previous = 0.0
   
    if previous == 0:
        arrow = ''
        color = color_schemes[current_theme]['text']
    else:
        pct_change = ((current - previous) / previous) * 100
        is_increasing = pct_change > 0
        
        if prefix == '$':
            arrow = ' ↑' if is_increasing else ' ↓'
            color = '#FF5252' if is_increasing else '#4CAF50'
        else:
            arrow = ' ↑' if is_increasing else ' ↓'
            color = '#4CAF50' if is_increasing else '#FF5252'
    
    formatted_value = f"{prefix}{current:,.2f}{suffix}"
    
    return html.Div([
        html.Span(formatted_value, 
                 style={'color': color_schemes[current_theme]['text']}),
        html.Span(arrow, 
                 style={
                     'color': color,
                     'marginLeft': '5px',
                     'fontSize': '20px',
                     'fontWeight': 'bold'
                 })
    ])

def generate_campaign_data_batch(num_records):
    global ad_data
    for _ in range(num_records):
        campaign_id = fake.uuid4()
        short_campaign_id = campaign_id.split('-')[0]
        ad_type = random.choice(ad_types)
        region = random.choice(regions)
        device = random.choice(devices)
        
        impressions = random.randint(1000, 100000)
        clicks = random.randint(10, int(impressions * 0.2))
        ctr = round((clicks / impressions) * 100, 2)
        cpc = round(random.uniform(0.1, 5.0), 2)
        conversions = random.randint(1, int(clicks * 0.1))
        revenue = round(conversions * random.uniform(5, 100), 2)
        spend = round(clicks * cpc, 2)
        roas = round(revenue / spend, 2) if spend > 0 else 0
        cpa = round(spend / conversions, 2) if conversions > 0 else 0
        conversion_rate = round((conversions / clicks) * 100, 2) if clicks > 0 else 0
        rpc = round(revenue / clicks, 2) if clicks > 0 else 0
        bounce_rate = round(random.uniform(30, 70), 2)
        roi = round(((revenue - spend) / spend) * 100, 2) if spend > 0 else 0
        day = random.choice(days)
        period = random.choice(periods)
        
        ad_data.append({
            "CampaignID": short_campaign_id,
            "FullCampaignID": campaign_id,
            "AdType": ad_type,
            "Region": region,
            "Device": device,
            "Impressions": impressions,
            "Clicks": clicks,
            "CTR": ctr,
            "CPC": cpc,
            "Conversions": conversions,
            "Revenue": revenue,
            "Spend": spend,
            "ROAS": roas,
            "RPC": rpc,
            "CPA": cpa,
            "ConversionRate": conversion_rate,
            "BounceRate": bounce_rate,
            "ROI": roi,
            "Period": day + " " + period,
        })

        if len(ad_data) > 50:
            ad_data.pop(0)

def stream_data():
    while True:
        generate_campaign_data_batch(5)
        time.sleep(60)

stream_thread = threading.Thread(target=stream_data, daemon=True)
stream_thread.start()

color_schemes = {
    'light': {
        'background': 'white',
        'text': 'black',

        'card_bg': 'rgba(255, 255, 255, 0.8)',
        'card_text': 'black',
        'plot_bg': 'white',
        'paper_bg': 'white'
    },
    'dark': {
        'background': '#1c1c1c',
        'text': 'white',
        'card_bg': 'rgba(28, 28, 28, 0.8)',
        'card_text': 'white',
        'plot_bg': '#1c1c1c',
        'paper_bg': '#1c1c1c'
    }
}

glass_effect_css = {
    'background': 'rgba(255, 255, 255, 0.1)',
    'border-radius': '20px',
    'backdrop-filter': 'blur(10px)',
    'padding': '15px',
    'margin': '5px'
}

app.layout = html.Div([
    html.Div([
        html.H1("Ad-Libs: Real-Time Advertising Analytics", className="text-center mb-4"),
        html.P("Auto-updating dashboard with real-time advertising analytics data (Updates Every 5 minutes).", className="text-center"),
        html.Div([
            html.Button("Light Theme", id='light-theme-btn', className="btn btn-light btn-sm mx-1"),
            html.Button("Dark Theme", id='dark-theme-btn', className="btn btn-dark btn-sm mx-1"),
        ], className="text-right mb-4")
    ], id='header', className="p-3"),
    
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H4("Average RPC", className="card-title"),
                    html.P("Revenue Per Click", className="card-text"),
                    html.H2(id='rpc', className="card-text"),
                ], className="card-body", id='rpc-card', style=glass_effect_css)
            ], className="card text-center mb-3"),
            
            html.Div([
                html.Div([
                    html.H4("Average CTR", className="card-title"),
                    html.P("Click Through Rate", className="card-text"),
                    html.H2(id='avg-ctr', className="card-text"),
                ], className="card-body", id='avg-ctr-card', style=glass_effect_css)
            ], className="card text-center mb-3"),
            
            html.Div([
                html.Div([
                    html.H4("Average CPC", className="card-title"),
                    html.P("Cost Per Click", className="card-text"),
                    html.H2(id='avg-cpc', className="card-text"),
                ], className="card-body", id='avg-cpc-card', style=glass_effect_css)
            ], className="card text-center mb-3"),
            
            html.Div([
                html.Div([
                    html.H4("Average CPA", className="card-title"),
                    html.P("Cost Per Acquisition", className="card-text"),
                    html.H2(id='avg-cpa', className="card-text"),
                ], className="card-body", id='avg-cpa-card', style=glass_effect_css)
            ], className="card text-center mb-3"),
            
            html.Div([
                html.Div([
                    html.H4("Peak Activity", className="card-title"),
                    html.P("Best Time to Advertise", className="card-text"),
                    html.H2(id='common-peak', className="card-text"),
                ], className="card-body", id='common-day-card', style=glass_effect_css)
            ], className="card text-center mb-3")
        ], className="d-flex justify-content-around"),
        
    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(id='roas-by-type'),
            ], className="col-md-6"),
            
            html.Div([
                dcc.Graph(id='ctr-by-device')
            ], className="col-md-6"),
        ], className="row mb-4"),
        
        html.Div([
            html.Div([
                dcc.Graph(id='metrics-trend')
            ], className="col-md-12")
        ], className="row"),
        
        html.Div([
            html.Div([
                html.H4("Clicks by Region", className="text-center"),
                dcc.Graph(id='region-map')
            ], className="col-md-8"),
            html.Div([
                dcc.Graph(id='top-countries')
            ], className="col-md-4")
            ], className="row")
    ], className="col-md-12")
    ], className="container-fluid"),

    dcc.Interval(
        id='update-interval',
        interval=300000,  
        n_intervals=0
    )
], id='main-container', className="container-fluid")

@app.callback(
    [
        dash.dependencies.Output('rpc', 'children'),
        dash.dependencies.Output('avg-ctr', 'children'),
        dash.dependencies.Output('avg-cpc', 'children'),
        dash.dependencies.Output('common-peak', 'children'),
        dash.dependencies.Output('avg-cpa', 'children'),
     
        dash.dependencies.Output('roas-by-type', 'figure'),
        dash.dependencies.Output('ctr-by-device', 'figure'),
        dash.dependencies.Output('metrics-trend', 'figure'),
        dash.dependencies.Output('region-map', 'figure'),
        dash.dependencies.Output('top-countries', 'figure'),  
        
        dash.dependencies.Output('header', 'style'),
        dash.dependencies.Output('main-container', 'style'),
        dash.dependencies.Output('rpc-card', 'style'),
        dash.dependencies.Output('avg-ctr-card', 'style'),
        dash.dependencies.Output('avg-cpc-card', 'style'),
        dash.dependencies.Output('common-day-card', 'style'),
        dash.dependencies.Output('avg-cpa-card', 'style')
    ],
    [
        dash.dependencies.Input('update-interval', 'n_intervals'),
        dash.dependencies.Input('light-theme-btn', 'n_clicks'),
        dash.dependencies.Input('dark-theme-btn', 'n_clicks'),
    ]
)

def update_dashboard(n, light_theme_btn, dark_theme_btn):
    global previous_kpis, current_theme
    
    if dash_ctx.triggered_id:
        if dash_ctx.triggered_id == 'light-theme-btn':
            current_theme = 'light'
        elif dash_ctx.triggered_id == 'dark-theme-btn':
            current_theme = 'dark'
    
    theme = current_theme
    
    if len(ad_data) == 0:
        return ['$0', '0%', '0', 'N/A', 'N/A', 
                go.Figure(), go.Figure(), go.Figure(), go.Figure(), go.Figure(),
                color_schemes[theme], color_schemes[theme], color_schemes[theme], color_schemes[theme], color_schemes[theme], color_schemes[theme]]

    df = pd.DataFrame(ad_data)
    
    rpc = f"${df['RPC'].mean():,.2f}"
    avg_ctr = f"{df['CTR'].mean():.2f}%"
    avg_cpc = f"${df['CPC'].mean():.2f}"
    common_peak = df['Period'].mode()[0]
    avg_cpa = f"${df['CPA'].mean():,.2f}"

    rpc_kpi = format_kpi_value(rpc, previous_kpis['rpc'], prefix='$')
    ctr_kpi = format_kpi_value(avg_ctr, previous_kpis['ctr'], suffix='%')
    cpc_kpi = format_kpi_value(avg_cpc, previous_kpis['cpc'], prefix='$')
    cpa_kpi = format_kpi_value(avg_cpa, previous_kpis['cpa'], prefix='$')

    previous_kpis = {
        'rpc': rpc,
        'ctr': avg_ctr,
        'cpc': avg_cpc,
        'cpa': avg_cpa
    }

    
    
    def add_info_icon(fig, theme, info_text, x_pos=0.98, y_pos=0.98):
        fig.add_annotation(
            text="ⓘ",
            xref="paper",
            yref="paper",
            x=x_pos,
            y=y_pos,
            showarrow=False,
            font=dict(
                size=16,
                color=color_schemes[theme]['text']
            ),
            hovertext=info_text,
            hoverlabel=dict(
                bgcolor=color_schemes[theme]['card_bg'],
                font_color=color_schemes[theme]['text']
            )
        )
    roas_by_type = go.Figure(data=[
        go.Bar(x=df.groupby('AdType')['ROAS'].sum().index, 
               y=df.groupby('AdType')['ROAS'].sum().values,
               marker_color=px.colors.qualitative.Pastel)
    ])
    roas_by_type.update_layout(
        plot_bgcolor=color_schemes[theme]['plot_bg'],
        paper_bgcolor=color_schemes[theme]['paper_bg'],
        font_color=color_schemes[theme]['text'],
        title="Average Return on Ad Spend (ROAS) by Ad Type",
    )

    add_info_icon(roas_by_type, theme,"ROAS shows how much money you make for every dollar spent on ads—the higher, the better!.")
    
    metrics_trend = go.Figure()

    metrics_trend.add_trace(
        go.Scatter(
            x=df.index,
            y=df['ConversionRate'],
            name='Conversion Rate',
            mode='lines+markers',
            line=dict(color=px.colors.qualitative.Pastel[0]),
            hovertemplate="Entry: %{x}<br>Conversion Rate: %{y:.2f}%<extra></extra>"
        )
    )

    metrics_trend.add_trace(
        go.Scatter(
            x=df.index,
            y=df['BounceRate'],
            name='Bounce Rate',
            mode='lines+markers',
            line=dict(color=px.colors.qualitative.Pastel[1]),
            hovertemplate="Entry: %{x}<br>Bounce Rate: %{y:.2f}%<extra></extra>"
        )
    )

    metrics_trend.update_layout(
        plot_bgcolor=color_schemes[theme]['plot_bg'],
        paper_bgcolor=color_schemes[theme]['paper_bg'],
        font_color=color_schemes[theme]['text'],
        title="Conversion and Bounce Rate Trends",
        xaxis_title="Data Points",
        yaxis_title="Rate (%)",
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    add_info_icon(
        metrics_trend, 
        theme,
        "Shows conversion and bounce rate trends over sequential data points. Higher conversion and lower bounce rates indicate better performance."
    )
 
    ctr_by_device = go.Figure(data=[
        go.Pie(
            labels=df.groupby('Device')['CTR'].mean().index,
            values=df.groupby('Device')['CTR'].mean().values,
            marker_colors=px.colors.qualitative.Pastel,
            textinfo='label+percent',
            hovertemplate="Device: %{label}<br>CTR: %{value:.2f}%<extra></extra>"
        )
    ])

    ctr_by_device.update_layout(
        plot_bgcolor=color_schemes[theme]['plot_bg'],
        paper_bgcolor=color_schemes[theme]['paper_bg'],
        font_color=color_schemes[theme]['text'],
        title="CTR by Device",
        showlegend=True
    )

    add_info_icon(
        ctr_by_device,
        theme,
        "Shows Click-Through Rate distribution across different devices. Larger segments indicate higher CTR for that device type."
    )
    
    region_sales = df.groupby('Region')['Clicks'].sum().reset_index()
    region_map = px.choropleth(
        region_sales,
        locations='Region',
        locationmode='country names',
        color='Clicks',
        color_continuous_scale='Viridis',
        projection='natural earth',
        hover_name='Region',
        hover_data={'Clicks': ':,.0f'}
    )
    
    region_map.update_layout(
    plot_bgcolor=color_schemes[theme]['plot_bg'],
    paper_bgcolor=color_schemes[theme]['paper_bg'],
    font_color=color_schemes[theme]['text'],
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='equirectangular',
        bgcolor=color_schemes[theme]['plot_bg'],
        resolution=50,
        showland=True,
        landcolor='lightgray',
        showcountries=True,
        countrycolor='white'
    ),

    dragmode=False,
    margin=dict(l=0, r=0, t=30, b=0),
    hovermode='closest'
    )
    add_info_icon(
        region_map,
        theme,
        "Shows which regions have the highest clicks. Hover over a region to see the number of clicks."
    )

    top_countries = go.Figure(data=[
        go.Bar(
            x=df.groupby('Region')['Clicks'].sum().nlargest(5).values,
            y=df.groupby('Region')['Clicks'].sum().nlargest(5).index,
            orientation='h',
            marker_color=px.colors.qualitative.Pastel[0]
        )
    ])

    top_countries.update_layout(
        plot_bgcolor=color_schemes[theme]['plot_bg'],
        paper_bgcolor=color_schemes[theme]['paper_bg'],
        font_color=color_schemes[theme]['text'],
        title="Top 5 Countries by Clicks",
        xaxis_title="Clicks",
        margin=dict(l=0, r=0, t=30, b=0),
        height=300
    )

    return [
        rpc_kpi, ctr_kpi, cpc_kpi, common_peak, cpa_kpi, 
        roas_by_type, ctr_by_device, metrics_trend, region_map, top_countries,
        {'backgroundColor': color_schemes[theme]['background'], 'color': color_schemes[theme]['text']},
        {'backgroundColor': color_schemes[theme]['background'], 'color': color_schemes[theme]['text']},
        {'backgroundColor': color_schemes[theme]['card_bg'], 'color': color_schemes[theme]['card_text']},
        {'backgroundColor': color_schemes[theme]['card_bg'], 'color': color_schemes[theme]['card_text']},
        {'backgroundColor': color_schemes[theme]['card_bg'], 'color': color_schemes[theme]['card_text']},
        {'backgroundColor': color_schemes[theme]['card_bg'], 'color': color_schemes[theme]['card_text']},
        {'backgroundColor': color_schemes[theme]['card_bg'], 'color': color_schemes[theme]['card_text']}
    ]

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
