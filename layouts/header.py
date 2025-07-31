import dash_mantine_components as dmc
from dash_iconify import DashIconify
from constants import LOGO
from flask_login import current_user

def create_header(data):
    return \
    dmc.AppShellHeader(
        dmc.Group(
            [
                dmc.Group(
                    [
                        dmc.Burger(
                            id="mobile-burger",
                            size="sm",
                            hiddenFrom="sm",
                            opened=False,
                        ),
                        dmc.Burger(
                            id="desktop-burger",
                            size="sm",
                            visibleFrom="sm",
                            opened=True,
                        ),
                        dmc.Image(src=f'/resource/{LOGO}', h=30, w=30),
                        dmc.Title("", c="black"),
                    ]
                ),
                dmc.Group(
                    [
                        dmc.Text(current_user.username if current_user.is_authenticated else "", fw=700),
                        dmc.ActionIcon(
                            DashIconify(icon="mdi:logout", width=20),
                            id="logout-button",
                            variant="subtle",
                            size="lg",
                            color="red",
                            #title="Cerrar sesión"
                        ),
                    ]
                )
                
            ],
            justify="space-between",
            style={"flex": 1},
            h="100%",
            px="sm",
        ),            
    )

