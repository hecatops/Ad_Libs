import dash
from dash import dcc, html
from dash import ctx as dash_ctx
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from faker import Faker
import time
import threading
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

app = dash.Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css'])
server = app.server
app.title = "Ad-Libs"

current_theme = 'light'
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
            arrow = ' ▲' if is_increasing else ' ▼'
            color = '#623440' if is_increasing else '#34623f'
        else:
            arrow = ' ▲' if is_increasing else ' ▼'
            color = '#34623f' if is_increasing else '#623440'
    
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
        'card_bg': '#0DCAF0',
        'card_text': 'black',
        'plot_bg': 'white',
        'paper_bg': 'white'
    },
    'dark': {
        'background': '#1c1c1c',
        'text': 'white',
        'card_bg': '#0DCAF0',
        'card_text': 'black',
        'plot_bg': '#1c1c1c',
        'paper_bg': '#1c1c1c'
    }
}

glass_effect_css = {
    'background': '#44a1a0',
    'border-radius': '5px',
    
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
        ], className="d-flex justify-content-around flex-wrap"),
        
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
                    html.H4("Revenue Forecast", className="text-center"),
                    dcc.Graph(id='forecast-plot')
                ], className="col-md-12 mb-4"),
                
                html.Div([
                    html.Button(
                        "Download Report",
                        id='download-report-btn',
                        className="btn btn-info btn-lg"
                    ),
                    dcc.Download(id='download-report')
                ], className="text-center mb-4")
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
        dash.dependencies.Output('forecast-plot', 'figure'),
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
        dash.dependencies.Input('download-report-btn', 'n_clicks')
    ]
)
def update_dashboard(n_interval, light_clicks, dark_clicks, download_clicks):
    global previous_kpis, current_theme
    
    if dash_ctx.triggered_id:
        if dash_ctx.triggered_id == 'light-theme-btn':
            current_theme = 'light'
        elif dash_ctx.triggered_id == 'dark-theme-btn':
            current_theme = 'dark'
    
    if len(ad_data) == 0:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            plot_bgcolor=color_schemes[current_theme]['plot_bg'],
            paper_bgcolor=color_schemes[current_theme]['paper_bg']
        )
        return ['$0', '0%', '$0', 'N/A', '$0'] + [empty_fig] * 5 + [
            {'backgroundColor': color_schemes[current_theme]['background'], 'color': color_schemes[current_theme]['text']},
            {'backgroundColor': color_schemes[current_theme]['background'], 'color': color_schemes[current_theme]['text']},
        ]

    df = pd.DataFrame(ad_data)
    
    # Calculate KPIs
    rpc = f"${df['RPC'].mean():.2f}"
    avg_ctr = f"{df['CTR'].mean():.2f}%"
    avg_cpc = f"${df['CPC'].mean():.2f}"
    common_peak = df['Period'].mode()[0]
    avg_cpa = f"${df['CPA'].mean():.2f}"

    # Format KPIs
    rpc_kpi = format_kpi_value(rpc, previous_kpis['rpc'], prefix='$')
    ctr_kpi = format_kpi_value(avg_ctr, previous_kpis['ctr'], suffix='%')
    cpc_kpi = format_kpi_value(avg_cpc, previous_kpis['cpc'], prefix='$')
    cpa_kpi = format_kpi_value(avg_cpa, previous_kpis['cpa'], prefix='$')

    # Update previous KPIs
    previous_kpis = {
        'rpc': rpc,
        'ctr': avg_ctr,
        'cpc': avg_cpc,
        'cpa': avg_cpa
    }

    # Create ROAS by Type plot
    roas_by_type = go.Figure(data=[
        go.Bar(
            x=df.groupby('AdType')['ROAS'].mean().index,
            y=df.groupby('AdType')['ROAS'].mean().values,
            marker_color=px.colors.sequential.Tealgrn
        )
    ])
    
    roas_by_type.update_layout(
        plot_bgcolor=color_schemes[current_theme]['plot_bg'],
        paper_bgcolor=color_schemes[current_theme]['paper_bg'],
        font_color=color_schemes[current_theme]['text'],
        title="Average ROAS by Ad Type"
    )

    # Create CTR by Device plot
    ctr_by_device = go.Figure(data=[
        go.Pie(
            labels=df.groupby('Device')['CTR'].mean().index,
            values=df.groupby('Device')['CTR'].mean().values,
            marker_colors=px.colors.sequential.Tealgrn,
            textinfo='label+percent'
        )
    ])

    ctr_by_device.update_layout(
        plot_bgcolor=color_schemes[current_theme]['plot_bg'],
        paper_bgcolor=color_schemes[current_theme]['paper_bg'],
        font_color=color_schemes[current_theme]['text'],
        title="CTR by Device"
    )

    # Create Metrics Trend plot
    metrics_trend = go.Figure()
    metrics_trend.add_trace(go.Scatter(
        x=df.index,
        y=df['ConversionRate'],
        name='Conversion Rate',
        mode='lines+markers',
        line=dict(color=px.colors.sequential.Tealgrn[0])
    ))
    
    metrics_trend.add_trace(go.Scatter(
        x=df.index,
        y=df['BounceRate'],
        name='Bounce Rate',
        mode='lines+markers',
        line=dict(color=px.colors.sequential.Tealgrn[1])
    ))

    metrics_trend.update_layout(
        plot_bgcolor=color_schemes[current_theme]['plot_bg'],
        paper_bgcolor=color_schemes[current_theme]['paper_bg'],
        font_color=color_schemes[current_theme]['text'],
        title="Conversion and Bounce Rate Trends",
        xaxis_title="Data Points",
        yaxis_title="Rate (%)"
    )

    # Create Region Map
    region_map = px.choropleth(
        df.groupby('Region')['Clicks'].sum().reset_index(),
        locations='Region',
        locationmode='country names',
        color='Clicks',
        color_continuous_scale='Tealgrn',
        projection='natural earth'
    )

    region_map.update_layout(
        plot_bgcolor=color_schemes[current_theme]['plot_bg'],
        paper_bgcolor=color_schemes[current_theme]['paper_bg'],
        font_color=color_schemes[current_theme]['text'],
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            bgcolor=color_schemes[current_theme]['plot_bg']
        )
    )

    # Create Top Countries plot
    top_countries = go.Figure(data=[
        go.Bar(
            x=df.groupby('Region')['Clicks'].sum().nlargest(5).values,
            y=df.groupby('Region')['Clicks'].sum().nlargest(5).index,
            orientation='h',
            marker_color=px.colors.sequential.Tealgrn[0]
        )
    ])

    top_countries.update_layout(
        plot_bgcolor=color_schemes[current_theme]['plot_bg'],
        paper_bgcolor=color_schemes[current_theme]['paper_bg'],
        font_color=color_schemes[current_theme]['text'],
        title="Top 5 Countries by Clicks",
        height=300
    )

    # Create Forecast plot
    forecast_data = pd.DataFrame({
        'ds': pd.date_range(start='2024-01-01', periods=len(df), freq='D'),
        'y': df['Revenue']
    })
    
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
    model.fit(forecast_data)
    
    future_dates = model.make_future_dataframe(periods=30)
    forecast = model.predict(future_dates)
    
    forecast_plot = go.Figure()
    forecast_plot.add_trace(go.Scatter(
        x=forecast['ds'][:len(df)],
        y=df['Revenue'],
        name='Historical Revenue',
        line_color='rgba(0,100,80,0.5)',
        mode='lines+markers'
    ))
    
    forecast_plot.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        name='Forecast',
        mode='lines',
        line_color='rgba(0,150,0,0.8)',
        line=dict(dash='dot')
    ))
    
    forecast_plot.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_upper'],
        fill=None,
        mode='lines',
        line_color='rgba(0,100,80,0.2)',
        name='Upper Bound'
    ))
    
    forecast_plot.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_lower'],
        fill='tonexty',
        mode='lines',
        line_color='rgba(0,100,80,0.2)',
        name='Lower Bound'
    ))
    
    forecast_plot.update_layout(
        plot_bgcolor=color_schemes[current_theme]['plot_bg'],
        paper_bgcolor=color_schemes[current_theme]['paper_bg'],
        font_color=color_schemes[current_theme]['text'],
        title="Revenue Forecast (30 Days)"
    )

    # Return all outputs
    return [
        rpc_kpi,
        ctr_kpi,
        cpc_kpi,
        common_peak,
        cpa_kpi,
        roas_by_type,
        ctr_by_device,
        metrics_trend,
        region_map,
        top_countries,
        forecast_plot,
        {'backgroundColor': color_schemes[current_theme]['background'], 'color': color_schemes[current_theme]['text']},
        {'backgroundColor': color_schemes[current_theme]['background'], 'color': color_schemes[current_theme]['text']},
        glass_effect_css,
        glass_effect_css,
        glass_effect_css,
        glass_effect_css,
        glass_effect_css
    ]

@app.callback(
    dash.dependencies.Output('download-report', 'data'),
    dash.dependencies.Input('download-report-btn', 'n_clicks'),
    prevent_initial_call=True
)

def generate_report(n_clicks):
    if n_clicks is None:
        return dash.no_update
    
    df = pd.DataFrame(ad_data)
    
    # Generate PDF report
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Add title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph("Ad Performance Report", title_style))
    story.append(Spacer(1, 12))
    
    # Add summary statistics
    metrics = [
        ["Metric", "Value"],
        ["Average Revenue", f"${df['Revenue'].mean():.2f}"],
        ["Average CTR", f"{df['CTR'].mean():.2f}%"],
        ["Average CPC", f"${df['CPC'].mean():.2f}"],
        ["Average ROAS", f"{df['ROAS'].mean():.2f}"],
        ["Total Conversions", f"{df['Conversions'].sum()}"],
        ["Total Impressions", f"{df['Impressions'].sum()}"],
        ["Total Clicks", f"{df['Clicks'].sum()}"],
        ["Total Spend", f"${df['Spend'].sum():.2f}"]
    ]
    
    table = Table(metrics)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 12))
    
    # Add visualizations
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x='AdType', y='ROAS', data=df, ax=ax)
    ax.set_title('Average ROAS by Ad Type')
    plt.tight_layout()
    imgdata = io.BytesIO()
    fig.savefig(imgdata, format='png')
    imgdata.seek(0)
    story.append(Image(imgdata, width=400, height=300))
    story.append(Spacer(1, 12))
    
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x='Device', y='CTR', data=df, ax=ax)
    ax.set_title('Average CTR by Device')
    plt.tight_layout()
    imgdata = io.BytesIO()
    fig.savefig(imgdata, format='png')
    imgdata.seek(0)
    story.append(Image(imgdata, width=400, height=300))
    story.append(Spacer(1, 12))
    
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.lineplot(x=df.index, y='Revenue', data=df, ax=ax)
    ax.set_title('Revenue Over Time')
    plt.tight_layout()
    imgdata = io.BytesIO()
    fig.savefig(imgdata, format='png')
    imgdata.seek(0)
    story.append(Image(imgdata, width=400, height=300))
    story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    
    return dcc.send_bytes(
        buffer.getvalue(),
        filename=f"ad_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
