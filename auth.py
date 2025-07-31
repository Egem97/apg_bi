import asyncio
import secrets
import yaml
from datetime import datetime, timedelta
from functools import wraps
from flask_login import LoginManager, UserMixin
from flask import request
from models import (
    DatabaseManager, 
    get_database_url, 
    get_user_by_username, 
    authenticate_user as auth_user_db,
    create_user_with_profile,
    User as UserModel,
    Company as CompanyModel
)
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Initialize Flask-Login
login_manager = LoginManager()

# Load configuration
def load_config():
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

# Initialize database connection
config = load_config()
if config and 'database' in config:
    db_config = config['database']
    DATABASE_URL = get_database_url(
        host=db_config['server'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['name']
    )
    db_manager = DatabaseManager(DATABASE_URL)
else:
    raise Exception("No se pudo cargar la configuración de la base de datos")

class User(UserMixin):
    """Flask-Login User class"""
    def __init__(self, user_id, username, email, company_id, is_admin=False, profile_data=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.company_id = company_id
        self.is_admin = is_admin
        self.profile_data = profile_data or {}

    @property
    def full_name(self):
        return f"{self.profile_data.get('first_name', '')} {self.profile_data.get('last_name', '')}"

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    try:
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def get_user():
            async with db_manager.get_session() as session:
                stmt = select(UserModel).options(
                    selectinload(UserModel.profile),
                    selectinload(UserModel.company)
                ).where(UserModel.id == int(user_id))
                
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    profile_data = {
                        'first_name': user.profile.first_name,
                        'last_name': user.profile.last_name,
                        'position': user.profile.position,
                        'department': user.profile.department,
                        'phone': user.profile.phone
                    }
                    
                    return User(
                        user_id=user.id,
                        username=user.username,
                        email=user.email,
                        company_id=user.company_id,
                        is_admin=user.is_admin,
                        profile_data=profile_data
                    )
                return None
        
        user = loop.run_until_complete(get_user())
        loop.close()
        return user
        
    except Exception as e:
        print(f"Error loading user {user_id}: {e}")
        return None

# Secret key for token generation
SECRET_KEY = secrets.token_hex(32)
TOKEN_EXPIRATION = timedelta(hours=1)

def get_db_connection():
    """Mantener compatibilidad - retorna el DatabaseManager"""
    return db_manager

def verify_password(stored_password, provided_password):
    """Verificar contraseña usando bcrypt (compatible con modelos SQLAlchemy)"""
    import bcrypt
    try:
        stored_bytes = stored_password.encode('utf-8')
        provided_bytes = provided_password.encode('utf-8')
        return bcrypt.checkpw(provided_bytes, stored_bytes)
    except Exception:
        return False

def create_token(user_id, username, company_id):
    """Create a secure token"""
    token_data = f"{user_id}:{username}:{company_id}:{datetime.utcnow().timestamp()}"
    import hashlib
    token = hashlib.sha256((token_data + SECRET_KEY).encode()).hexdigest()
    return f"{token}:{token_data}"

def verify_token(token):
    """Verify a token and return the user data if valid"""
    try:
        import hashlib
        token_hash, token_data = token.split(':', 1)
        user_id, username, company_id, timestamp = token_data.split(':')
        
        # Verify token hash
        expected_hash = hashlib.sha256((token_data + SECRET_KEY).encode()).hexdigest()
        if token_hash != expected_hash:
            return None
            
        # Check token expiration
        token_time = datetime.fromtimestamp(float(timestamp))
        if datetime.utcnow() - token_time > TOKEN_EXPIRATION:
            return None
            
        return {
            'user_id': int(user_id),
            'username': username,
            'company_id': int(company_id)
        }
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None

def create_user(username, password, first_name, last_name, email, phone, company_id=1, is_admin=False):
    """Create a new user with profile using PostgreSQL"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def create():
            async with db_manager.get_session() as session:
                try:
                    user = await create_user_with_profile(
                        session=session,
                        username=username,
                        email=email,
                        password=password,
                        company_id=company_id,
                        first_name=first_name,
                        last_name=last_name,
                        phone=phone,
                        is_admin=is_admin
                    )
                    return user is not None
                except Exception as e:
                    print(f"Error creating user: {e}")
                    return False
        
        result = loop.run_until_complete(create())
        loop.close()
        return result
        
    except Exception as e:
        print(f"Error in create_user: {e}")
        return False

def authenticate_user(username, password):
    """Authenticate a user and return a token if successful"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def auth():
            async with db_manager.get_session() as session:
                user = await auth_user_db(session, username, password)
                
                if user:
                    # Generate token
                    token = create_token(user.id, user.username, user.company_id)
                    return {
                        'token': token, 
                        'user_id': user.id, 
                        'company_id': user.company_id,
                        'username': user.username,
                        'email': user.email,
                        'is_admin': user.is_admin,
                        'full_name': user.profile.full_name if user.profile else f"{username}"
                    }
                return None
        
        result = loop.run_until_complete(auth())
        loop.close()
        return result
        
    except Exception as e:
        print(f"Error in authenticate_user: {e}")
        return None

def get_user_by_username_sync(username):
    """Get user by username synchronously"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def get_user():
            async with db_manager.get_session() as session:
                return await get_user_by_username(session, username)
        
        result = loop.run_until_complete(get_user())
        loop.close()
        return result
        
    except Exception as e:
        print(f"Error getting user by username: {e}")
        return None

def get_user_companies(user_id):
    """Get all companies associated with a user"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def get_companies():
            async with db_manager.get_session() as session:
                # Obtener el usuario con su empresa
                stmt = select(UserModel).options(
                    selectinload(UserModel.company)
                ).where(UserModel.id == user_id)
                
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user and user.company:
                    return [{
                        'id': user.company.id,
                        'name': user.company.name,
                        'description': user.company.description,
                        'email': user.company.email,
                        'website': user.company.website
                    }]
                return []
        
        result = loop.run_until_complete(get_companies())
        loop.close()
        return result
        
    except Exception as e:
        print(f"Error getting user companies: {e}")
        return []

def token_required(f):
    """Decorator to require a valid token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return {'message': 'Token is missing'}, 401
        
        payload = verify_token(token)
        if not payload:
            return {'message': 'Invalid or expired token'}, 401
        
        # Add user info to the request context
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated

