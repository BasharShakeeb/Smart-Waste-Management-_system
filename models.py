# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash
# from sqlalchemy.orm import validates

# db = SQLAlchemy()

# # Database Models with Enhanced Relationships
# class User(db.Model):
#     __tablename__ = 'users'
    
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     email = db.Column(db.String(120), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(255), nullable=False)
#     role = db.Column(db.String(20), nullable=False, default='driver')  # 'admin', 'manager', 'driver'
#     name = db.Column(db.String(100), nullable=False)
#     phone = db.Column(db.String(20))
#     is_active = db.Column(db.Boolean, default=True)
#     last_login = db.Column(db.DateTime)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships
#     driver_profile = db.relationship('Driver', backref='user', uselist=False, cascade='all, delete-orphan')
#     created_tasks = db.relationship('Task', foreign_keys='Task.created_by', backref='creator')
    
#     @validates('email')
#     def validate_email(self, key, email):
#         if '@' not in email:
#             raise ValueError('Invalid email address')
#         return email
    
#     @validates('role')
#     def validate_role(self, key, role):
#         if role not in ['admin', 'manager', 'driver']:
#             raise ValueError('Invalid role')
#         return role
    
#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)
    
#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'username': self.username,
#             'email': self.email,
#             'role': self.role,
#             'name': self.name,
#             'phone': self.phone,
#             'is_active': self.is_active,
#             'last_login': self.last_login.isoformat() if self.last_login else None,
#             'created_at': self.created_at.isoformat(),
#             'updated_at': self.updated_at.isoformat()
#         }

# class Bin(db.Model):
#     __tablename__ = 'bins'
    
#     id = db.Column(db.Integer, primary_key=True)
#     bin_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
#     location = db.Column(db.String(200), nullable=False)
#     address = db.Column(db.Text)
#     latitude = db.Column(db.Float)
#     longitude = db.Column(db.Float)
#     capacity = db.Column(db.Float, default=100.0)  # in liters
#     bin_type = db.Column(db.String(50), default='general')  # general, recyclable, organic, hazardous
#     fill_level = db.Column(db.Integer, default=0)  # 0-100%
#     temperature = db.Column(db.Float)
#     humidity = db.Column(db.Float)
#     angle = db.Column(db.Float)  # tilt sensor
#     battery_level = db.Column(db.Integer, default=100)
#     signal_strength = db.Column(db.Integer)  # WiFi/cellular signal
#     status = db.Column(db.String(20), default='active')  # active, inactive, maintenance, error
#     last_collected = db.Column(db.DateTime)
#     last_emptied = db.Column(db.DateTime)
#     installation_date = db.Column(db.DateTime, default=datetime.utcnow)
#     maintenance_due = db.Column(db.DateTime)
#     notes = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships
#     task_bins = db.relationship('TaskBin', backref='bin', cascade='all, delete-orphan')
#     sensor_readings = db.relationship('SensorReading', backref='bin', cascade='all, delete-orphan')
    
#     @validates('fill_level')
#     def validate_fill_level(self, key, fill_level):
#         if fill_level < 0 or fill_level > 100:
#             raise ValueError('Fill level must be between 0 and 100')
#         return fill_level
    
#     @validates('battery_level')
#     def validate_battery_level(self, key, battery_level):
#         if battery_level < 0 or battery_level > 100:
#             raise ValueError('Battery level must be between 0 and 100')
#         return battery_level
    
#     @validates('bin_type')
#     def validate_bin_type(self, key, bin_type):
#         valid_types = ['general', 'recyclable', 'organic', 'hazardous']
#         if bin_type not in valid_types:
#             raise ValueError(f'Bin type must be one of: {valid_types}')
#         return bin_type
    
#     @property
#     def is_full(self):
#         return self.fill_level >= 80
    
#     @property
#     def needs_maintenance(self):
#         return (self.maintenance_due and self.maintenance_due <= datetime.utcnow()) or \
#                self.battery_level < 20 or \
#                self.status == 'error'
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'bin_id': self.bin_id,
#             'location': self.location,
#             'address': self.address,
#             'latitude': self.latitude,
#             'longitude': self.longitude,
#             'capacity': self.capacity,
#             'bin_type': self.bin_type,
#             'fill_level': self.fill_level,
#             'battery_level': self.battery_level,
#             'status': self.status,
#             'is_full': self.is_full,
#             'needs_maintenance': self.needs_maintenance,
#             'last_collected': self.last_collected.isoformat() if self.last_collected else None,
#             'last_emptied': self.last_emptied.isoformat() if self.last_emptied else None,
#             'installation_date': self.installation_date.isoformat(),
#             'maintenance_due': self.maintenance_due.isoformat() if self.maintenance_due else None,
#             'notes': self.notes,
#             'created_at': self.created_at.isoformat(),
#             'updated_at': self.updated_at.isoformat()
#         }

# class Driver(db.Model):
#     __tablename__ = 'drivers'
    
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
#     license_number = db.Column(db.String(50), unique=True)
#     license_expiry = db.Column(db.Date)
#     vehicle_id = db.Column(db.String(50), db.ForeignKey('vehicles.id'), unique=True)
#     vehicle_type = db.Column(db.String(50), nullable=False)
#     emergency_contact = db.Column(db.String(100))
#     emergency_phone = db.Column(db.String(20))
#     status = db.Column(db.String(20), default='offline')  # online, offline, busy, break, unavailable
#     current_location_lat = db.Column(db.Float)
#     current_location_lng = db.Column(db.Float)
#     last_location_update = db.Column(db.DateTime)
#     shift_start = db.Column(db.DateTime)
#     shift_end = db.Column(db.DateTime)
#     rating = db.Column(db.Float, default=5.0)
#     total_collections = db.Column(db.Integer, default=0)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships
#     vehicle = db.relationship('Vehicle', backref='current_driver')
#     assigned_tasks = db.relationship('Task', foreign_keys='Task.driver_id', backref='assigned_driver')
    
#     @validates('status')
#     def validate_status(self, key, status):
#         valid_statuses = ['online', 'offline', 'busy', 'break', 'unavailable']
#         if status not in valid_statuses:
#             raise ValueError(f'Status must be one of: {valid_statuses}')
#         return status
    
#     @validates('rating')
#     def validate_rating(self, key, rating):
#         if rating < 0 or rating > 5:
#             raise ValueError('Rating must be between 0 and 5')
#         return rating
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'user_id': self.user_id,
#             'user_name': self.user.name if self.user else None,
#             'user_email': self.user.email if self.user else None,
#             'license_number': self.license_number,
#             'license_expiry': self.license_expiry.isoformat() if self.license_expiry else None,
#             'vehicle_id': self.vehicle_id,
#             'vehicle_name': self.vehicle.vehicle_id if self.vehicle else 'No Vehicle Assigned',
#             'emergency_phone': self.emergency_phone,
#             'status': self.status,
#             'current_location_lat': self.current_location_lat,
#             'current_location_lng': self.current_location_lng,
#             'last_location_update': self.last_location_update.isoformat() if self.last_location_update else None,
#             'shift_start': self.shift_start.isoformat() if self.shift_start else None,
#             'shift_end': self.shift_end.isoformat() if self.shift_end else None,
#             'rating': self.rating,
#             'total_collections': self.total_collections,
#             'created_at': self.created_at.isoformat(),
#             'updated_at': self.updated_at.isoformat()
#         }

# class Vehicle(db.Model):
#     __tablename__ = 'vehicles'
    
#     id = db.Column(db.Integer, primary_key=True)
#     vehicle_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
#     vehicle_type = db.Column(db.String(50), nullable=False)
#     make = db.Column(db.String(50))
#     model = db.Column(db.String(50))
#     year = db.Column(db.Integer)
#     license_plate = db.Column(db.String(20), unique=True)
#     capacity = db.Column(db.Float)  # in cubic meters
#     fuel_type = db.Column(db.String(20), default='diesel')  # diesel, electric, hybrid
#     fuel_level = db.Column(db.Float)  # percentage
#     mileage = db.Column(db.Float)
#     last_maintenance = db.Column(db.DateTime)
#     next_maintenance = db.Column(db.DateTime)
#     insurance_expiry = db.Column(db.Date)
#     status = db.Column(db.String(20), default='available')  # available, in_use, maintenance, out_of_service
#     gps_enabled = db.Column(db.Boolean, default=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships
#     tasks = db.relationship('Task', backref='vehicle')
    
#     @validates('status')
#     def validate_status(self, key, status):
#         valid_statuses = ['available', 'in_use', 'maintenance', 'out_of_service']
#         if status not in valid_statuses:
#             raise ValueError(f'Status must be one of: {valid_statuses}')
#         return status
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'vehicle_id': self.vehicle_id,
#             'vehicle_type': self.vehicle_type,
#             'make': self.make,
#             'model': self.model,
#             'year': self.year,
#             'license_plate': self.license_plate,
#             'capacity': self.capacity,
#             'fuel_type': self.fuel_type,
#             'fuel_level': self.fuel_level,
#             'mileage': self.mileage,
#             'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
#             'next_maintenance': self.next_maintenance.isoformat() if self.next_maintenance else None,
#             'insurance_expiry': self.insurance_expiry.isoformat() if self.insurance_expiry else None,
#             'status': self.status,
#             'gps_enabled': self.gps_enabled,
#             'current_driver': self.current_driver.user.name if self.current_driver else None,
#             'created_at': self.created_at.isoformat(),
#             'updated_at': self.updated_at.isoformat()
#         }

# class Task(db.Model):
#     __tablename__ = 'tasks'
    
#     id = db.Column(db.Integer, primary_key=True)
#     task_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
#     title = db.Column(db.String(200))
#     description = db.Column(db.Text)
#     driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
#     vehicle_id = db.Column(db.Integer(50), db.ForeignKey('vehicles.id'), nullable=False)
#     created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     route_name = db.Column(db.String(100))
#     estimated_duration = db.Column(db.Integer)  # in minutes
#     estimated_distance = db.Column(db.Float)  # in kilometers
#     actual_duration = db.Column(db.Integer)
#     actual_distance = db.Column(db.Float)
#     status = db.Column(db.String(20), default='pending')  # pending, assigned, in_progress, completed, cancelled
#     priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
#     scheduled_time = db.Column(db.DateTime)
#     started_time = db.Column(db.DateTime)
#     completed_time = db.Column(db.DateTime)
#     notes = db.Column(db.Text)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships
#     task_bins = db.relationship('TaskBin', backref='task', cascade='all, delete-orphan')
    
#     @validates('status')
#     def validate_status(self, key, status):
#         valid_statuses = ['pending', 'assigned', 'in_progress', 'completed', 'cancelled']
#         if status not in valid_statuses:
#             raise ValueError(f'Status must be one of: {valid_statuses}')
#         return status
    
#     @validates('priority')
#     def validate_priority(self, key, priority):
#         valid_priorities = ['low', 'normal', 'high', 'urgent']
#         if priority not in valid_priorities:
#             raise ValueError(f'Priority must be one of: {valid_priorities}')
#         return priority
    
#     @property
#     def total_bins(self):
#         return db.session.query(TaskBin).filter_by(task_id=self.id).count()
    
#     @property
#     def completed_bins(self):
#         return db.session.query(TaskBin).filter_by(task_id=self.id, status='collected').count()
    
#     @property
#     def completion_percentage(self):
#         total = self.total_bins
#         if total == 0:
#             return 0
#         return (self.completed_bins / total) * 100
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'task_id': self.task_id,
#             'title': self.title,
#             'description': self.description,
#             'driver_id': self.driver_id,
#             'driver_name': self.assigned_driver.user.name if self.assigned_driver else None,
#             'vehicle_id': self.vehicle_id,
#             'vehicle_name': self.vehicle.vehicle_id if self.vehicle else None,
#             'created_by': self.created_by,
#             'creator_name': self.creator.name if self.creator else None,
#             'route_name': self.route_name,
#             'estimated_duration': self.estimated_duration,
#             'estimated_distance': self.estimated_distance,
#             'actual_duration': self.actual_duration,
#             'actual_distance': self.actual_distance,
#             'status': self.status,
#             'priority': self.priority,
#             'total_bins': self.total_bins,
#             'completed_bins': self.completed_bins,
#             'completion_percentage': self.completion_percentage,
#             'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
#             'started_time': self.started_time.isoformat() if self.started_time else None,
#             'completed_time': self.completed_time.isoformat() if self.completed_time else None,
#             'notes': self.notes,
#             'created_at': self.created_at.isoformat(),
#             'updated_at': self.updated_at.isoformat()
#         }

# class TaskBin(db.Model):
#     __tablename__ = 'task_bins'
    
#     id = db.Column(db.Integer, primary_key=True)
#     task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
#     bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=False)
#     sequence_order = db.Column(db.Integer)  # order in the route
#     status = db.Column(db.String(20), default='pending')  # pending, collected, skipped, failed
#     collected_time = db.Column(db.DateTime)
#     fill_level_before = db.Column(db.Integer)
#     fill_level_after = db.Column(db.Integer)
#     weight_collected = db.Column(db.Float)  # in kg
#     notes = db.Column(db.Text)
#     photo_url = db.Column(db.String(500))  # evidence photo
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     @validates('status')
#     def validate_status(self, key, status):
#         valid_statuses = ['pending', 'collected', 'skipped', 'failed']
#         if status not in valid_statuses:
#             raise ValueError(f'Status must be one of: {valid_statuses}')
#         return status
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'task_id': self.task_id,
#             'bin_id': self.bin_id,
#             'bin_identifier': self.bin.bin_id if self.bin else None,
#             'bin_location': self.bin.location if self.bin else None,
#             'sequence_order': self.sequence_order,
#             'status': self.status,
#             'collected_time': self.collected_time.isoformat() if self.collected_time else None,
#             'fill_level_before': self.fill_level_before,
#             'fill_level_after': self.fill_level_after,
#             'weight_collected': self.weight_collected,
#             'notes': self.notes,
#             'photo_url': self.photo_url,
#             'created_at': self.created_at.isoformat(),
#             'updated_at': self.updated_at.isoformat()
#         }

# class SensorReading(db.Model):
#     __tablename__ = 'sensor_readings'
    
#     id = db.Column(db.Integer, primary_key=True)
#     bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=False)
#     fill_level = db.Column(db.Integer, nullable=False)
#     temperature = db.Column(db.Float)
#     humidity = db.Column(db.Float)
#     battery_level = db.Column(db.Integer)
#     signal_strength = db.Column(db.Integer)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'bin_id': self.bin_id,
#             'bin_identifier': self.bin.bin_id if self.bin else None,
#             'fill_level': self.fill_level,
#             'temperature': self.temperature,
#             'humidity': self.humidity,
#             'battery_level': self.battery_level,
#             'signal_strength': self.signal_strength,
#             'timestamp': self.timestamp.isoformat()
#         }
from enum import unique
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Nullable
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates

db = SQLAlchemy()

# Database Models (corrected types and FK consistency)
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='driver')
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    driver_profile = db.relationship('Driver', backref='user', uselist=False, cascade='all, delete-orphan')
    created_tasks = db.relationship('Task', foreign_keys='Task.created_by', backref='creator')

    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError('Invalid email address')
        return email

    @validates('role')
    def validate_role(self, key, role):
        if role not in ['admin', 'manager', 'driver']:
            raise ValueError('Invalid role')
        return role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'name': self.name,
            'phone': self.phone,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Bin(db.Model):
    __tablename__ = 'bins'

    id = db.Column(db.Integer, primary_key=True)
    bin_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    location = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    capacity = db.Column(db.Float, default=100.0)
    bin_type = db.Column(db.String(50), default='general')
    fill_level = db.Column(db.Integer, default=0)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    angle = db.Column(db.Float)
    battery_level = db.Column(db.Integer, default=100)
    signal_strength = db.Column(db.Integer)
    status = db.Column(db.String(20), default='active')
    last_collected = db.Column(db.DateTime)
    last_emptied = db.Column(db.DateTime)
    installation_date = db.Column(db.DateTime, default=datetime.utcnow)
    maintenance_due = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    task_bins = db.relationship('TaskBin', backref='bin', cascade='all, delete-orphan')
    sensor_readings = db.relationship('SensorReading', backref='bin', cascade='all, delete-orphan')

    @validates('fill_level')
    def validate_fill_level(self, key, fill_level):
        if fill_level is not None and (fill_level < 0 or fill_level > 100):
            raise ValueError('Fill level must be between 0 and 100')
        return fill_level

    @validates('battery_level')
    def validate_battery_level(self, key, battery_level):
        if battery_level is not None and (battery_level < 0 or battery_level > 100):
            raise ValueError('Battery level must be between 0 and 100')
        return battery_level

    @validates('bin_type')
    def validate_bin_type(self, key, bin_type):
        valid_types = ['general', 'recyclable', 'organic', 'hazardous']
        if bin_type not in valid_types:
            raise ValueError(f'Bin type must be one of: {valid_types}')
        return bin_type

    @property
    def is_full(self):
        return self.fill_level is not None and self.fill_level >= 80

    @property
    def needs_maintenance(self):
        return (self.maintenance_due and self.maintenance_due <= datetime.utcnow()) or \
               (self.battery_level is not None and self.battery_level < 20) or \
               self.status == 'error'

    def to_dict(self):
        return {
            'id': self.id,
            'bin_id': self.bin_id,
            'location': self.location,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'capacity': self.capacity,
            'bin_type': self.bin_type,
            'fill_level': self.fill_level,
            'battery_level': self.battery_level,
            'status': self.status,
            'is_full': self.is_full,
            'needs_maintenance': self.needs_maintenance,
            'last_collected': self.last_collected.isoformat() if self.last_collected else None,
            'last_emptied': self.last_emptied.isoformat() if self.last_emptied else None,
            'installation_date': self.installation_date.isoformat(),
            'maintenance_due': self.maintenance_due.isoformat() if self.maintenance_due else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    id = db.Column(db.Integer, primary_key=True)
    # vehicle_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    vehicle_type = db.Column(db.String(50), nullable=False)
    make = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    license_plate = db.Column(db.String(20), unique=True)
    capacity = db.Column(db.Float)
    fuel_type = db.Column(db.String(20), default='diesel')
    fuel_level = db.Column(db.Float)
    mileage = db.Column(db.Float)
    last_maintenance = db.Column(db.DateTime)
    next_maintenance = db.Column(db.DateTime)
    insurance_expiry = db.Column(db.Date)
    status = db.Column(db.String(20), default='available')
    gps_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # tasks = db.relationship('Task', backref='vehicle')

    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = ['available', 'in_use', 'maintenance', 'out_of_service']
        if status not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return status

    def to_dict(self):
        # current_driver may be None or a Driver instance depending on relationship
        current_driver = self.current_driver if not isinstance(self.current_driver, list) else (self.current_driver[0] if self.current_driver else None)
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'vehicle_type': self.vehicle_type,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'license_plate': self.license_plate,
            'capacity': self.capacity,
            'fuel_type': self.fuel_type,
            'fuel_level': self.fuel_level,
            'mileage': self.mileage,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'next_maintenance': self.next_maintenance.isoformat() if self.next_maintenance else None,
            'insurance_expiry': self.insurance_expiry.isoformat() if self.insurance_expiry else None,
            'status': self.status,
            'gps_enabled': self.gps_enabled,
            'current_driver': current_driver.user.name if current_driver and current_driver.user else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Driver(db.Model):
    __tablename__ = 'drivers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    license_number = db.Column(db.String(50), unique=True)
    license_expiry = db.Column(db.Date)
    vehicle_id = db.Column(db.Integer, unique=True)
    vehicle_type = db.Column(db.String(50), nullable=False)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    status = db.Column(db.String(20), default='offline')
    current_location_lat = db.Column(db.Float)
    current_location_lng = db.Column(db.Float)
    last_location_update = db.Column(db.DateTime)
    shift_start = db.Column(db.DateTime)
    shift_end = db.Column(db.DateTime)
    rating = db.Column(db.Float, default=5.0)
    total_collections = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # vehicle = db.relationship('Vehicle', backref='current_driver', uselist=False)
    assigned_tasks = db.relationship('Task', foreign_keys='Task.driver_id', backref='assigned_driver')

    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = ['online', 'offline', 'busy', 'break', 'unavailable']
        if status not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return status

    @validates('rating')
    def validate_rating(self, key, rating):
        if rating < 0 or rating > 5:
            raise ValueError('Rating must be between 0 and 5')
        return rating

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else None,
            'user_email': self.user.email if self.user else None,
            'license_number': self.license_number,
            'license_expiry': self.license_expiry.isoformat() if self.license_expiry else None,
            'vehicle_id': self.vehicle_id,
            # 'vehicle_name': self.vehicle.vehicle_id if self.vehicle else 'No Vehicle Assigned',
            'emergency_phone': self.emergency_phone,
            'status': self.status,
            'current_location_lat': self.current_location_lat,
            'current_location_lng': self.current_location_lng,
            'last_location_update': self.last_location_update.isoformat() if self.last_location_update else None,
            'shift_start': self.shift_start.isoformat() if self.shift_start else None,
            'shift_end': self.shift_end.isoformat() if self.shift_end else None,
            'rating': self.rating,
            'total_collections': self.total_collections,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    route_name = db.Column(db.String(100))
    estimated_duration = db.Column(db.Integer)
    estimated_distance = db.Column(db.Float)
    actual_duration = db.Column(db.Integer)
    actual_distance = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
    priority = db.Column(db.String(20), default='normal')
    scheduled_time = db.Column(db.DateTime)
    started_time = db.Column(db.DateTime)
    completed_time = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    task_bins = db.relationship('TaskBin', backref='task', cascade='all, delete-orphan')

    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = ['pending', 'assigned', 'in_progress', 'completed', 'cancelled']
        if status not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return status

    @validates('priority')
    def validate_priority(self, key, priority):
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if priority not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return priority

    @property
    def total_bins(self):
        return db.session.query(TaskBin).filter_by(task_id=self.id).count()

    @property
    def completed_bins(self):
        return db.session.query(TaskBin).filter_by(task_id=self.id, status='collected').count()

    @property
    def completion_percentage(self):
        total = self.total_bins
        if total == 0:
            return 0
        return (self.completed_bins / total) * 100

    # def to_dict(self):
    #     return {
    #         'id': self.id,
    #         'task_id': self.task_id,
    #         'title': self.title,
    #         'description': self.description,
    #         'driver_id': self.driver_id,
    #         'driver_name': self.assigned_driver.user.name if self.assigned_driver else None,
    #         'vehicle_id': self.vehicle_id,
    #         'vehicle_name': self.vehicle.vehicle_id if self.vehicle else None,
    #         'created_by': self.created_by,
    #         'creator_name': self.creator.name if self.creator else None,
    #         'route_name': self.route_name,
    #         'estimated_duration': self.estimated_duration,
    #         'estimated_distance': self.estimated_distance,
    #         'actual_duration': self.actual_duration,
    #         'actual_distance': self.actual_distance,
    #         'status': self.status,
    #         'priority': self.priority,
    #         'total_bins': self.total_bins,
    #         'completed_bins': self.completed_bins,
    #         'completion_percentage': self.completion_percentage,
    #         'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
    #         'started_time': self.started_time.isoformat() if self.started_time else None,
    #         'completed_time': self.completed_time.isoformat() if self.completed_time else None,
    #         'notes': self.notes,
    #         'created_at': self.created_at.isoformat(),
    #         'updated_at': self.updated_at.isoformat()
    #     }

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'driver_id': self.driver_id,
            'driver_name': self.assigned_driver.user.name if self.assigned_driver else None,
            'vehicle_id': None,        # ما عاد في عمود vehicle_id
            'vehicle_name': None,      # ما عاد في علاقة vehicle
            'created_by': self.created_by,
            'creator_name': self.creator.name if self.creator else None,
            'route_name': self.route_name,
            'estimated_duration': self.estimated_duration,
            'estimated_distance': self.estimated_distance,
            'actual_duration': self.actual_duration,
            'actual_distance': self.actual_distance,
            'status': self.status,
            'priority': self.priority,
            'total_bins': self.total_bins,
            'completed_bins': self.completed_bins,
            'completion_percentage': self.completion_percentage,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'started_time': self.started_time.isoformat() if self.started_time else None,
            'completed_time': self.completed_time.isoformat() if self.completed_time else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }



class TaskBin(db.Model):
    __tablename__ = 'task_bins'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=False)
    sequence_order = db.Column(db.Integer)
    status = db.Column(db.String(20), default='pending')
    collected_time = db.Column(db.DateTime)
    fill_level_before = db.Column(db.Integer)
    fill_level_after = db.Column(db.Integer)
    weight_collected = db.Column(db.Float)
    notes = db.Column(db.Text)
    photo_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @validates('status')
    def validate_status(self, key, status):
        valid_statuses = ['pending', 'collected', 'skipped', 'failed']
        if status not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return status

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'bin_id': self.bin_id,
            'bin_identifier': self.bin.bin_id if self.bin else None,
            'bin_location': self.bin.location if self.bin else None,
            'sequence_order': self.sequence_order,
            'status': self.status,
            'collected_time': self.collected_time.isoformat() if self.collected_time else None,
            'fill_level_before': self.fill_level_before,
            'fill_level_after': self.fill_level_after,
            'weight_collected': self.weight_collected,
            'notes': self.notes,
            'photo_url': self.photo_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class SensorReading(db.Model):
    __tablename__ = 'sensor_readings'

    id = db.Column(db.Integer, primary_key=True)
    bin_id = db.Column(db.Integer, db.ForeignKey('bins.id'), nullable=False)
    fill_level = db.Column(db.Integer, nullable=False)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    battery_level = db.Column(db.Integer)
    signal_strength = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'bin_id': self.bin_id,
            'bin_identifier': self.bin.bin_id if self.bin else None,
            'fill_level': self.fill_level,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'battery_level': self.battery_level,
            'signal_strength': self.signal_strength,
            'timestamp': self.timestamp.isoformat()
        }