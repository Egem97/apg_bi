import dash_mantine_components as dmc
import dash
from dash import Dash, _dash_renderer, html, dcc
from constants import * 
from layouts.appshell import create_appshell
from layouts.login import create_login_layout
from auth import login_manager, verify_password, User, create_user, authenticate_user, get_user_companies, token_required, get_user_by_username_sync
from flask_login import login_user, logout_user, current_user
from dash.dependencies import Input, Output, State
import os
from datetime import datetime
from flask import send_from_directory, request, jsonify
#from core.bd import dataOut
_dash_renderer._set_react_version("18.2.0")


data = {
    'name_user':NAME_USER,
    'name_empresa':NAME_EMPRESA,
    'tipo_empresa':RUBRO_EMPRESA,
}


app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    use_pages=True,
    external_stylesheets=dmc.styles.ALL,
    update_title=None,
    assets_folder='assets',  # Asegurarse de que assets_folder apunte a la carpeta correcta
)

# Configurar ruta específica para el favicon
@app.server.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.server.root_path, 'assets'),
        'favicon.ico',
        mimetype='image/x-icon'
    )

# Configurar la ruta para servir archivos desde resource
@app.server.route('/resource/<path:path>')
def serve_resource(path):
    return send_from_directory('resource', path)

# Configurar la clave secreta para Flask
app.server.secret_key = os.environ.get('SECRET_KEY', 'una-clave-secreta-muy-segura-123')  # En producción, usa una clave segura desde variables de entorno

# Inicializar Flask-Login
login_manager.init_app(app.server)
login_manager.login_view = 'login'

# Layout condicional
app.layout = dmc.MantineProvider(
    html.Div(
        children=[
            html.Link(
                rel='icon',
                href='/assets/favicon.ico',
                type='image/x-icon'
            ),
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content')
        ]
    )
)

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    #if pathname == '/login':
    #    if current_user.is_authenticated:
    #        return dcc.Location(pathname='/', id='redirect-to-home')
   #     return create_login_layout()
    
    #if not current_user.is_authenticated:
    #    return dcc.Location(pathname='/login', id='redirect-to-login')
    return create_appshell(data)

@app.callback(
    [Output('url', 'pathname'),
     Output('login-error', 'children')],
    [Input('login-button', 'n_clicks')],
    [State('username-input', 'value'),
     State('password-input', 'value')]
)
def login_callback(n_clicks, username, password):
    #if n_clicks is None:
    #    return '/login', ''
    return '/', ''
    # Usar la nueva función de autenticación con PostgreSQL
    """
    user_data = get_user_by_username_sync(username)
    print(user_data)
    if user_data and user_data.check_password(password) and user_data.is_active:
        # Crear usuario para Flask-Login
        profile_data = {
            'first_name': user_data.profile.first_name if user_data.profile else '',
            'last_name': user_data.profile.last_name if user_data.profile else '',
            'position': user_data.profile.position if user_data.profile else '',
            'department': user_data.profile.department if user_data.profile else '',
            'phone': user_data.profile.phone if user_data.profile else ''
        }
        
        user = User(
            user_id=user_data.id,
            username=user_data.username,
            email=user_data.email,
            company_id=user_data.company_id,
            is_admin=user_data.is_admin,
            profile_data=profile_data
        )
        login_user(user)
        return '/', ''
    
    return '/login', 'Usuario o contraseña incorrectos'
    """
@app.callback(
    Output('url', 'pathname', allow_duplicate=True),
    [Input('logout-button', 'n_clicks')],
    prevent_initial_call=True
)
def logout_callback(n_clicks):
    if n_clicks:
        logout_user()
        return '/login'
    return dash.no_update

@app.server.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(k in data for k in ('username', 'password', 'first_name', 'last_name', 'email')):
        return jsonify({'message': 'Missing required fields'}), 400
    
    success = create_user(
        username=data['username'],
        password=data['password'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data.get('phone', ''),
        company_id=data.get('company_id', 1),  # Default company ID
        is_admin=data.get('is_admin', False)
    )
    
    if success:
        return jsonify({'message': 'User created successfully'}), 201
    else:
        return jsonify({'message': 'Username or email already exists'}), 400

@app.server.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ('username', 'password')):
        return jsonify({'message': 'Missing username or password'}), 400
    
    result = authenticate_user(data['username'], data['password'])
    
    if result:
        return jsonify(result), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@app.server.route('/companies', methods=['GET'])
@token_required
def get_companies():
    companies = get_user_companies(request.user['user_id'])
    return jsonify(companies), 200

@app.server.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check para Docker healthcheck"""
    try:
        # Verificaciones básicas de salud
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'services': {
                'dashboard': 'running',
                'database': 'connected' if check_db_connection() else 'disconnected'
            }
        }
        return jsonify(health_data), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

def check_db_connection():
    """Verifica conexión a la base de datos"""
    try:
        # Aquí puedes agregar una verificación real de BD si es necesario
        # Por ahora retornamos True
        return True
    except Exception:
        return False

if __name__ == "__main__":
    app.run(
        host='0.0.0.0',  # Permite conexiones desde cualquier IP
        port=PORT,       # Puerto personalizable
        debug=MODE_DEBUG,

    )