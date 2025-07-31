from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from datetime import datetime
import bcrypt
from typing import Optional

# Base para todos los modelos
Base = declarative_base()

class Company(Base):
    """Modelo de Empresa"""
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    website = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relación con usuarios
    users = relationship("User", back_populates="company")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"


class User(Base):
    """Modelo de Usuario"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Foreign Key a Company
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    
    # Relaciones
    company = relationship("Company", back_populates="users")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def set_password(self, password: str):
        """Establece la contraseña hasheada"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verifica la contraseña"""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', company='{self.company.name if self.company else None}')>"


class UserProfile(Base):
    """Modelo de Perfil de Usuario"""
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    position = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    birth_date = Column(DateTime, nullable=True)
    hire_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Key a User (Relación uno a uno)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # Relación
    user = relationship("User", back_populates="profile")
    
    @property
    def full_name(self) -> str:
        """Retorna el nombre completo"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, full_name='{self.full_name}', user='{self.user.username if self.user else None}')>"


class DatabaseManager:
    """Manejador de base de datos para operaciones asíncronas"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self):
        """Crea todas las tablas en la base de datos"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self):
        """Elimina todas las tablas de la base de datos"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    def get_session(self) -> AsyncSession:
        """Retorna una sesión asíncrona"""
        return self.async_session()
    
    async def close(self):
        """Cierra la conexión del engine"""
        await self.engine.dispose()


# Funciones de utilidad para operaciones CRUD

async def create_company(session: AsyncSession, name: str, description: str = None, 
                        email: str = None, phone: str = None, address: str = None, 
                        website: str = None) -> Company:
    """Crea una nueva empresa"""
    company = Company(
        name=name,
        description=description,
        email=email,
        phone=phone,
        address=address,
        website=website
    )
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return company


async def create_user_with_profile(session: AsyncSession, username: str, email: str, 
                                 password: str, company_id: int, first_name: str, 
                                 last_name: str, position: str = None, 
                                 department: str = None, phone: str = None,
                                 is_admin: bool = False) -> User:
    """Crea un usuario con su perfil asociado"""
    
    # Crear usuario
    user = User(
        username=username,
        email=email,
        company_id=company_id,
        is_admin=is_admin
    )
    user.set_password(password)
    
    # Crear perfil
    profile = UserProfile(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        position=position,
        department=department
    )
    
    # Asociar perfil al usuario
    user.profile = profile
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    """Obtiene un usuario por su username incluyendo perfil y empresa"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    stmt = select(User).options(
        selectinload(User.profile),
        selectinload(User.company)
    ).where(User.username == username)
    
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def authenticate_user(session: AsyncSession, username: str, password: str) -> Optional[User]:
    """Autentica un usuario verificando username y contraseña"""
    user = await get_user_by_username(session, username)
    if user and user.check_password(password) and user.is_active:
        # Actualizar último login
        user.last_login = datetime.utcnow()
        await session.commit()
        return user
    return None


# Ejemplo de configuración de base de datos
def get_database_url(host: str, port: int, user: str, password: str, database: str) -> str:
    """Genera la URL de conexión para SQLAlchemy async"""
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}" 