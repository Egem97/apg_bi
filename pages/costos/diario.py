import dash
import dash_mantine_components as dmc
from constants import PAGE_TITLE_PREFIX
from core.dashboard_factory import dashboard_factory, DashboardConfig
from config.dashboard_configs import COSTOS_DIARIOS_CONFIG

dash.register_page(__name__, "/costos-diarios", title=PAGE_TITLE_PREFIX + "Costos Diarios")
dmc.add_figure_templates(default="mantine_light")

# Crear dashboard usando configuración declarativa
config = DashboardConfig(COSTOS_DIARIOS_CONFIG)
layout = dashboard_factory.create_dashboard(config)
