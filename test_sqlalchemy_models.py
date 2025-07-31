import asyncio
import sys
from models import (
    DatabaseManager, 
    create_company, 
    create_user_with_profile, 
    get_user_by_username, 
    authenticate_user,
    get_database_url
)

async def test_database_models():
    """Prueba completa de los modelos de base de datos"""
    
    # Configuración de la base de datos (usando la misma del test_postgres.py)
    config = {
        "host": "dpg-d22mj7qdbo4c73fdg33g-a.oregon-postgres.render.com",
        "port": 5432,
        "user": "dream_postgres_user",
        "password": "uvXLm5j7CtNLiWbgoALLGZgm03DFcAX5",
        "database": "dream_postgres"
    }
    
    # Crear URL de conexión para SQLAlchemy
    database_url = get_database_url(**config)
    
    print("=" * 70)
    print("🚀 INICIANDO PRUEBAS DE MODELOS SQLALCHEMY CON POSTGRESQL")
    print("=" * 70)
    
    # Inicializar el manejador de base de datos
    db_manager = DatabaseManager(database_url)
    
    try:
        print("🔧 Creando tablas en la base de datos...")
        await db_manager.create_tables()
        print("✅ Tablas creadas exitosamente!")
        
        # Obtener sesión de base de datos
        async with db_manager.get_session() as session:
            
            # 1. Crear empresas
            print("\n📊 Creando empresas de prueba...")
            
            company1 = await create_company(
                session=session,
                name="Tech Solutions Inc.",
                description="Empresa de soluciones tecnológicas",
                email="contact@techsolutions.com",
                phone="+1-555-0123",
                address="123 Tech Street, Silicon Valley, CA",
                website="https://techsolutions.com"
            )
            print(f"✅ Empresa creada: {company1.name} (ID: {company1.id})")
            
            company2 = await create_company(
                session=session,
                name="DataCorp Analytics",
                description="Análisis de datos y business intelligence",
                email="info@datacorp.com", 
                phone="+1-555-0456",
                website="https://datacorp.com"
            )
            print(f"✅ Empresa creada: {company2.name} (ID: {company2.id})")
            
            # 2. Crear usuarios con perfiles
            print("\n👥 Creando usuarios con perfiles...")
            
            user1 = await create_user_with_profile(
                session=session,
                username="admin_user",
                email="admin@techsolutions.com",
                password="admin123",
                company_id=company1.id,
                first_name="Juan",
                last_name="Pérez",
                position="Administrador de Sistema",
                department="IT",
                phone="+1-555-1001",
                is_admin=True
            )
            print(f"✅ Usuario admin creado: {user1.username} ")
            
            user2 = await create_user_with_profile(
                session=session,
                username="data_analyst",
                email="maria@datacorp.com",
                password="analyst456",
                company_id=company2.id,
                first_name="María",
                last_name="González",
                position="Analista de Datos",
                department="Analytics",
                phone="+1-555-1002"
            )
            print(f"✅ Usuario analista creado: {user2.username}")
            
            user3 = await create_user_with_profile(
                session=session,
                username="developer",
                email="carlos@techsolutions.com", 
                password="dev789",
                company_id=company1.id,
                first_name="Carlos",
                last_name="Rodríguez",
                position="Desarrollador Senior",
                department="Desarrollo",
                phone="+1-555-1003"
            )
            print(f"✅ Usuario desarrollador creado: {user3.username}")
            
            # 3. Probar consultas
            print("\n🔍 Probando consultas de usuarios...")
            
            # Buscar usuario por username
            found_user = await get_user_by_username(session, "admin_user")
            if found_user:
                print(f"✅ Usuario encontrado: {found_user.username}")
                
            # 4. Probar autenticación
            print("\n🔐 Probando autenticación de usuarios...")
            
            # Autenticación exitosa
            auth_user = await authenticate_user(session, "admin_user", "admin123")
            if auth_user:
                print(f"✅ Autenticación exitosa: {auth_user.username}")
                print(f"   Último login: {auth_user.last_login}")
            else:
                print("❌ Fallo en autenticación")
            
            # Autenticación fallida (contraseña incorrecta)
            auth_fail = await authenticate_user(session, "admin_user", "wrong_password")
            if not auth_fail:
                print("✅ Autenticación falló correctamente con contraseña incorrecta")
            
            # 5. Mostrar información de todas las empresas y usuarios
            print("\n📋 Resumen de datos creados:")
            
            from sqlalchemy import select
            from sqlalchemy.orm import selectinload
            
            # Obtener todas las empresas con sus usuarios
            companies_stmt = select(company1.__class__).options(
                selectinload(company1.__class__.users).selectinload(user1.__class__.profile)
            )
            companies_result = await session.execute(companies_stmt)
            companies = companies_result.scalars().all()
            
            for company in companies:
                print(f"\n🏢 Empresa: {company.name}")
                print(f"   Descripción: {company.description}")
                print(f"   Email: {company.email}")
                print(f"   Usuarios ({len(company.users)}):")
                
                for user in company.users:
                    print(f"     • {user.profile.full_name} ({user.username})")
                    print(f"       Posición: {user.profile.position}")
                    print(f"       Departamento: {user.profile.department}")
                    print(f"       Admin: {'Sí' if user.is_admin else 'No'}")
            
        print("\n🎉 Todas las pruebas completadas exitosamente!")
        
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n🧹 Limpiando base de datos...")
        try:
            # Opcional: descomentar para limpiar las tablas después de las pruebas
            # await db_manager.drop_tables()
            # print("✅ Tablas eliminadas")
            print("ℹ️  Las tablas se mantienen para revisión (descomenta drop_tables para limpiar)")
        except Exception as e:
            print(f"⚠️  Error al limpiar: {e}")
        
        await db_manager.close()
        print("🔌 Conexión cerrada")
        
    print("=" * 70)


async def demo_password_hashing():
    """Demostración del sistema de hash de contraseñas"""
    print("\n🔒 DEMOSTRACIÓN DE HASH DE CONTRASEÑAS")
    print("-" * 50)
    
    from models import User
    
    # Crear usuario temporal para demostrar hashing
    user = User(username="demo", email="demo@example.com", company_id=1)
    
    # Establecer contraseña
    original_password = "mi_contraseña_segura_123"
    user.set_password(original_password)
    
    print(f"Contraseña original: {original_password}")
    print(f"Hash almacenado: {user.password_hash}")
    
    # Verificar contraseña correcta
    is_correct = user.check_password(original_password)
    print(f"Verificación correcta: {is_correct}")
    
    # Verificar contraseña incorrecta
    is_incorrect = user.check_password("contraseña_incorrecta")
    print(f"Verificación incorrecta: {is_incorrect}")


if __name__ == "__main__":
    try:
        # Ejecutar demostración de hash
        asyncio.run(demo_password_hashing())
        
        # Ejecutar pruebas principales
        asyncio.run(test_database_models())
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Pruebas interrumpidas por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 