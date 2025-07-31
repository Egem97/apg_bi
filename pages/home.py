import dash
import dash_mantine_components as dmc
import requests
from dash import html
from dash_iconify import DashIconify
from constants import PAGE_TITLE_PREFIX
from dash import Dash, dcc, html, Input, Output, dash_table, callback
import dash_mantine_components as dmc
import plotly.express as px
#from core.bd import dataOut

dash.register_page(
    __name__,
    "/",
    title= PAGE_TITLE_PREFIX+ "Home",
    #description="Official documentation and collection of ready-made Plotly Dash Components created using Dash "
    #"Mantine Components. Dash Mantine Components is an extensive UI components library for Plotly Dash "
    #"with more than 90 components and supports dark theme natively.",
)

#df = dataOut()
layout = dmc.Container(
    fluid=True,
    px=40,
    children=[
        dmc.Title("Bienvenido al Dashboard Corporativo", order=1, mt=30),

        dmc.Text(
            "Consulta información clave de las áreas Comercial, Producción y Finanzas desde una sola interfaz.",
            size="md",
            c="dimmed",
            mt=10,
            mb=30
        ),

        dmc.Group(
            #position="center",
            gap="xl",
            children=[
                dmc.Paper(
                    withBorder=True,
                    shadow="md",
                    radius="md",
                    p="xl",
                    style={"width": 300},
                    children=[
                        DashIconify(icon="mdi:chart-line", width=40, height=40),
                        dmc.Text("Comercial", size="lg", fw=700),
                        dmc.Text("Ventas, KPIs, clientes clave"),
                        dmc.Button("Ir a Comercial", variant="light", fullWidth=True, mt=10)
                    ]
                ),
                dmc.Paper(
                    withBorder=True,
                    shadow="md",
                    radius="md",
                    p="xl",
                    style={"width": 300},
                    children=[
                        DashIconify(icon="mdi:factory", width=40, height=40),
                        dmc.Text("Producción", size="lg", fw=500),
                        dmc.Text("Órdenes y líneas de producción"),
                        dmc.Button("Ir a Producción", variant="light", fullWidth=True, mt=10)
                    ]
                ),
                dmc.Paper(
                    withBorder=True,
                    shadow="md",
                    radius="md",
                    p="xl",
                    style={"width": 300},
                    children=[
                        DashIconify(icon="mdi:cash", width=40, height=40),
                        dmc.Text("Finanzas", size="lg", fw=500),
                        dmc.Text("Ingresos, gastos, proyecciones"),
                        dmc.Button("Ir a Finanzas", variant="light", fullWidth=True, mt=10,)
                    ]
                )
            ]
        )
    ]
)
"""
@callback(
    Output("line_chart", "figure"),
    Input("stock-dropdown", "value"),
)
def select_stocks(stocks):
    fig = px.line(data_frame=data, x="date", y=stocks, template="simple_white")
    fig.update_layout(
        margin=dict(t=50, l=25, r=25, b=25), yaxis_title="Price", xaxis_title="Date"
    )
    return fig


layout = html.Div(
    [
        dmc.Container(
            size="lg",
            mt=30,
            children = [
                dmc.Text("Version Info:"),
            ]
        ) 
    ]
)  
"""