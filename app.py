print("Starting app.py...")
from flask import Flask
print("Imported Flask")
from flask_socketio import SocketIO
print("Imported SocketIO")
import os
import threading
import time
import random
from datetime import datetime

# Import models and utilities
print("Importing models...")
from models import db, User, Bin, Driver
print("Imported models")
from websocket_events import init_socketio_events
print("Imported websocket_events")

# Import route blueprints
print("Importing routes...")
from routes.main_routes import main_routes
from routes.user_routes import user_api
from routes.driver_routes import driver_api
from routes.bin_routes import bin_api
from routes.task_routes import task_api
# from routes.driver_routes import driver_api # Duplicate import
print("Imported routes")


app = Flask(__name__)

# Database Configuration - MySQL Setup
# You can change these settings or set them as environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '8655090027bashar')  # Set your MySQL password here
DB_NAME = 'collect_me_iot'  # Database name
# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'collectme-iot-secret-key-2024')

# Try MySQL first, fallback to SQLite if MySQL is not available
# Force SQLite for local running
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collect_me_iot.db'
# print("⚠️  Using SQLite database")
try:
    # MySQL Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'echo': False  # Set to True for SQL debugging
    }
    print(f"🔗 Configured to use MySQL database: {DB_NAME}")
    print(f"📍 MySQL Server: {DB_HOST}:{DB_PORT}")
    print(f"👤 MySQL User: {DB_USER}")
except Exception as e:
    # Fallback to SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collect_me_iot.db'
    print("⚠️  MySQL configuration failed, using SQLite fallback")
    print(f"Error: {e}")

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


# # Simulate real-time updates
# def start_background_tasks():
#     def simulate_updates():
#         while True:
#             time.sleep(30)  # Update every 30 seconds
#             with app.app_context():
#                 # Simulate bin fill level changes for bins that exist
#                 bins = Bin.query.all()
#                 for bin_obj in bins:
#                     # Random fill level change
#                     change = random.randint(-2, 8)
#                     new_fill_level = max(0, min(100, bin_obj.fill_level + change))
#                     bin_obj.fill_level = new_fill_level
                    
#                     # Emit update to all connected clients
#                     socketio.emit('bin_status_update', {
#                         'bin_id': bin_obj.bin_id,
#                         'fill_level': new_fill_level,
#                         'status': 'critical' if new_fill_level >= 90 else 'warning' if new_fill_level >= 80 else 'normal'
#                     })
                
#                 try:
#                     db.session.commit()
#                 except Exception as e:
#                     print(f'Error updating bins: {e}')
#                     db.session.rollback()
    
#     threading.Thread(target=simulate_updates, daemon=True).start()

if __name__ == '__main__':
    print("Starting app initialization...")
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created.")
        
        # Create admin user if it doesn't exist
        print("Checking for admin user...")
        admin_user = User.query.filter_by(email='admin@collectme.com').first()
        if not admin_user:
            print("Creating admin user...")
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
    
    # # Start background simulation tasks
    # start_background_tasks()
    
    # Run with SocketIO
    print("Starting SocketIO server on port 5000...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    print("SocketIO server exited.")