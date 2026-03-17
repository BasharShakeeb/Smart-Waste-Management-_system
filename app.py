from flask import Flask, session, request, redirect, url_for, jsonify
from flask_socketio import SocketIO
import os   
import threading
import time
import random
from datetime import datetime
from i18n import get_translation_func, get_locale_dir, SUPPORTED_LOCALES, DEFAULT_LOCALE
from models import db, User, Bin, Driver
from websocket_events import init_socketio_events
from routes.main_routes import main_routes
from routes.user_routes import user_api
from routes.driver_routes import driver_api
from routes.bin_routes import bin_api
from routes.task_routes import task_api


app = Flask(__name__)

# Database Configuration - PostgreSQL Setup
# Priority: 1. DATABASE_URL (for Render/Cloud), 2. Individual variables, 3. Defaults
DATABASE_URL = os.getenv('DATABASE_URL')
DB_HOST = os.getenv('DB_HOST', 'dpg-d6sqonk50q8c73fp4740-a') # Updated default to your Render host
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'collect_me_iot_user') # Updated default to your Render user
DB_NAME = os.getenv('DB_NAME', 'collect_me_iot')
DB_PASSWORD = os.getenv('DB_PASSWORD', '8655090027') # We will keep a placeholder, preferably set in Render Env

if DATABASE_URL:
    print("DEBUG: Using DATABASE_URL for connection")
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    print(f"DEBUG: Using individual variables for connection. Host: {DB_HOST}")
    # If DB_PASSWORD is not in env, we use the one you provided earlier
    pwd = os.getenv('DB_PASSWORD', '8655090027') 
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{pwd}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'collectme-iot-secret-key-2024')

# Try PostgreSQL connection test
try:
    import psycopg2
    conn_uri = app.config['SQLALCHEMY_DATABASE_URI']
    # Removing any options for pure psycopg2 test
    simple_uri = conn_uri.split('?')[0] if '?' in conn_uri else conn_uri
    test_conn = psycopg2.connect(simple_uri)
    test_conn.close()
    print("DEBUG: PostgreSQL connection successful!")
    
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'echo': False
    }
except Exception as e:
    print(f"CRITICAL: PostgreSQL connection failed: {e}")
    # Only fall back to SQLite if NOT on Render (to avoid hidden failures)
    if os.getenv('RENDER'):
         print("CRITICAL: We are on Render but DB failed. Application will likely crash.")
    else:
        print("DEBUG: Local environment detected. Falling back to SQLite.")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collect_me_iot.db'


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Register blueprints
app.register_blueprint(main_routes)
app.register_blueprint(user_api)
app.register_blueprint(driver_api)
app.register_blueprint(bin_api)
app.register_blueprint(task_api)

# Initialize WebSocket events
init_socketio_events(socketio)


# --- i18n: inject t() and locale helpers into every template ---
@app.context_processor
def inject_i18n():
    locale = session.get("locale", DEFAULT_LOCALE)
    t = get_translation_func(locale)
    return dict(t=t, locale=locale, locale_dir=get_locale_dir(locale))


@app.route("/set-locale/<locale>")
def set_locale(locale):
    if locale in SUPPORTED_LOCALES:
        session["locale"] = locale
    return redirect(request.referrer or url_for("main.dashboard"))


@app.route("/api/translations")
def api_translations():
    """Expose JS-relevant translations so client-side code can use them."""
    locale = session.get("locale", DEFAULT_LOCALE)
    t = get_translation_func(locale)
    from i18n import _load_messages
    messages = _load_messages(locale)
    return jsonify(messages.get("js", {}))



# Database initialization and admin creation
with app.app_context():
    try:
        db.create_all()
        admin_user = User.query.filter_by(email='admin@collectme.com').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@collectme.com',
                role='admin',
                name='System Administrator',
                is_active=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            print('Created admin user: admin@collectme.com / admin123')
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Error during startup database sync: {e}")

if __name__ == '__main__':
    # Run with SocketIO locally
    print("Starting SocketIO server on port 5000...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
    print("SocketIO server exited.")