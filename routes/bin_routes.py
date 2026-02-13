from flask import Blueprint, request, jsonify, session
from datetime import datetime
from models import db, Bin, TaskBin, Task, SensorReading
from utils import admin_required, driver_required, validate_json_data

bin_api = Blueprint('bin_api', __name__)

# Bins API
@bin_api.route('/api/bins', methods=['GET'])
@driver_required
def api_get_bins():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        bin_type = request.args.get('bin_type')
        fill_level_min = request.args.get('fill_level_min', type=int)
        fill_level_max = request.args.get('fill_level_max', type=int)
        location = request.args.get('location')
        
        query = Bin.query
        
        if status:
            query = query.filter(Bin.status == status)
        
        if bin_type:
            query = query.filter(Bin.bin_type == bin_type)
        
        if fill_level_min is not None:
            query = query.filter(Bin.fill_level >= fill_level_min)
        
        if fill_level_max is not None:
            query = query.filter(Bin.fill_level <= fill_level_max)
        
        if location:
            query = query.filter(Bin.location.contains(location))
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        bins = [bin.to_dict() for bin in pagination.items]
        
        return jsonify({
            'bins': bins,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bin_api.route('/api/bins', methods=['POST'])
@admin_required
@validate_json_data(['bin_id', 'location'])
def api_create_bin():
    try:
        data = request.get_json()
        
        # Check if bin_id already exists
        if Bin.query.filter_by(bin_id=data['bin_id']).first():
            return jsonify({'error': 'Bin ID already exists'}), 400
        
        bin_obj = Bin(
            bin_id=data['bin_id'],
            location=data['location'],
            address=data.get('address'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            capacity=data.get('capacity', 100.0),
            bin_type=data.get('bin_type', 'general'),
            fill_level=data.get('fill_level', 0),
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            battery_level=data.get('battery_level', 100),
            status=data.get('status', 'active'),
            notes=data.get('notes')
        )
        
        db.session.add(bin_obj)
        db.session.commit()
        
        return jsonify({'message': 'Bin created successfully', 'bin': bin_obj.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bin_api.route('/api/bins/<int:bin_id>', methods=['GET'])
@driver_required
def api_get_bin(bin_id):
    try:
        bin_obj = Bin.query.get_or_404(bin_id)
        return jsonify({'bin': bin_obj.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bin_api.route('/api/bins/<int:bin_id>', methods=['PUT'])
@admin_required
def api_update_bin(bin_id):
    try:
        bin_obj = Bin.query.get_or_404(bin_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Update fields
        updatable_fields = [
            'location', 'address', 'latitude', 'longitude', 'capacity', 'bin_type',
            'fill_level', 'temperature', 'humidity', 'battery_level', 'status',
            'maintenance_due', 'notes'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(bin_obj, field, data[field])
        
        bin_obj.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Bin updated successfully', 'bin': bin_obj.to_dict()})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bin_api.route('/api/bins/<int:bin_id>', methods=['DELETE'])
@admin_required
def api_delete_bin(bin_id):
    try:
        print("bin_id:", bin_id)
        bin_obj = Bin.query.get_or_404(bin_id)
        print("bin_obj:", bin_obj)
        
        db.session.delete(bin_obj)
        db.session.commit()
        
        return jsonify({'message': 'Bin deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bin_api.route('/api/bins/<int:bin_id>/sensor-readings', methods=['POST'])
def api_add_sensor_reading(bin_id):
    try:
        bin_obj = Bin.query.get_or_404(bin_id)
        data = request.get_json()
        print("data:", data)
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Create sensor reading
        reading = SensorReading(
            bin_id=bin_id,
            fill_level=data.get('fill_level', bin_obj.fill_level),
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            battery_level=data.get('battery_level', bin_obj.battery_level),
            signal_strength=data.get('signal_strength')
        )
        
        # Update bin with latest readings
        bin_obj.fill_level = reading.fill_level
        bin_obj.temperature = reading.temperature
        bin_obj.humidity = reading.humidity
        bin_obj.battery_level = reading.battery_level
        bin_obj.signal_strength = reading.signal_strength
        bin_obj.updated_at = datetime.utcnow()
        
        db.session.add(reading)
        db.session.commit()
        
        return jsonify({'message': 'Sensor reading added successfully', 'reading': reading.to_dict()}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API endpoints for full bins and driver bins
@bin_api.route('/api/bins/full')
def api_full_bins():
    """API endpoint to get full bins data for task creation"""
    if 'user_id' not in session or session['role'] not in ['admin', 'manager']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    full_bins = Bin.query.filter(Bin.fill_level >= 80, Bin.status == 'active').all()
    
    bins_data = []
    for bin_obj in full_bins:
        bins_data.append({
            'id': bin_obj.id,
            'bin_id': bin_obj.bin_id,
            'location': bin_obj.location,
            'latitude': float(bin_obj.latitude),
            'longitude': float(bin_obj.longitude),
            'fill_level': bin_obj.fill_level,
            'bin_type': bin_obj.bin_type,
            'status': bin_obj.status,
            'last_collected': bin_obj.last_collected.isoformat() if bin_obj.last_collected else None
        })
    
    return jsonify({'bins': bins_data})

@bin_api.route('/api/driver/bins')
def api_driver_bins():
    """API endpoint to get bins for the current driver's tasks"""
    if 'user_id' not in session or session['role'] != 'driver':
        return jsonify({'error': 'Unauthorized'}), 401
    
    from models import User
    user = User.query.get(session['user_id'])
    if not user.driver_profile:
        return jsonify({'error': 'Driver profile not found'}), 404
    
    # Get driver's current tasks
    tasks = Task.query.filter_by(
        driver_id=user.driver_profile.id
    ).filter(
        Task.status.in_(['pending', 'assigned', 'in_progress'])
    ).all()
    
    bins_data = []
    for task in tasks:
        for task_bin in task.task_bins:
            bin_obj = task_bin.bin
            bins_data.append({
                'id': bin_obj.id,
                'bin_id': bin_obj.bin_id,
                'location': bin_obj.location,
                'latitude': float(bin_obj.latitude),
                'longitude': float(bin_obj.longitude),
                'fill_level': bin_obj.fill_level,
                'bin_type': bin_obj.bin_type,
                'status': task_bin.status,
                'task_id': task.id
            })
    
    return jsonify({'bins': bins_data})