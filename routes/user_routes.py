from flask import Blueprint, request, jsonify, session
from datetime import datetime
from models import Vehicle, db, User, Driver
from utils import admin_required, validate_json_data

user_api = Blueprint('user_api', __name__)

# Utility route for fixing driver profiles
@user_api.route('/admin/fix-driver-profiles', methods=['POST'])
@admin_required
def fix_driver_profiles():
    """Utility route to create missing driver profiles for users with role='driver'"""
    try:
        # Find users with role='driver' but no driver_profile
        users_without_profiles = User.query.filter(
            User.role == 'driver',
            ~User.id.in_(db.session.query(Driver.user_id))
        ).all()
        
        created_count = 0
        for user in users_without_profiles:
            driver = Driver(
                user_id=user.id,
                license_number=f'DL{user.id:06d}',  # Generate a default license number
                status='offline'
            )
            db.session.add(driver)
            created_count += 1
        
        db.session.commit()
        
        return jsonify({
            'message': f'Created {created_count} missing driver profiles',
            'created_count': created_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Users API
@user_api.route('/api/users', methods=['GET'])
@admin_required
def api_get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        role = request.args.get('role')
        search = request.args.get('search')
        
        query = User.query
        
        if role:
            query = query.filter(User.role == role)
        
        if search:
            query = query.filter(
                db.or_(
                    User.name.contains(search),
                    User.email.contains(search),
                    User.username.contains(search)
                )
            )
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        users = [user.to_dict() for user in pagination.items]
        
        return jsonify({
            'users': users,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/api/users', methods=['POST'])
@admin_required
@validate_json_data(['username', 'email', 'password', 'name', 'role' ])
def api_create_user():
    try:
        data = request.get_json()
        print("Data:", data)
        
        print(data)
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        user = User(
            username=data['username'],
            email=data['email'],
            name=data['name'],
            role=data['role'],
            phone=data.get('phone'),
            is_active=data.get('is_active', True)

        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create driver profile if role is driver
        if data['role'] == 'driver':
            driver = Driver(
                user_id=user.id,
                license_number=data.get('license_number'),
                vehicle_type=data.get('vehicle_type'),
                vehicle_id = data.get('vehicle_id'),
                
            )   
            db.session.add(driver)
            db.session.commit()
        
        return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/api/users/<int:user_id>', methods=['GET'])
@admin_required
def api_get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({'user': user.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def api_update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Store old role to check for changes
        old_role = user.role
        
        # Update fields
        for field in ['username', 'email', 'name', 'role', 'phone', 'is_active']:
            if field in data:
                
                if field == 'email' and data[field] != user.email:
                    if User.query.filter_by(email=data[field]).first():
                        return jsonify({'error': 'Email already exists'}), 400
                
                if field == 'username' and data[field] != user.username:
                    if User.query.filter_by(username=data[field]).first():
                        return jsonify({'error': 'Username already exists'}), 400
                
                setattr(user, field, data[field])
        
        if 'password' in data:
            user.set_password(data['password'])
       
        # Handle role changes
        if 'role' in data and old_role != data['role']:
            if data['role'] == 'driver' and not user.driver_profile:
                # Create driver profile when role changed to driver
                driver = Driver(
                    user_id=user.id,
                    license_number=data.get('license_number'),
                    emergency_contact=data.get('emergency_contact'),
                    emergency_phone=data.get('emergency_phone'),
                    vehicle_type=data.get('vehicle_type'),
                    vehicle_id = data.get('vehicle_id'),
                    status=data.get('status')
                )
                db.session.add(driver)
            elif old_role == 'driver' and data['role'] != 'driver' and user.driver_profile:
                # Remove driver profile when role changed from driver
                db.session.delete(user.driver_profile)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'User updated successfully', 'user': user.to_dict()})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_api.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def api_delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        
        # Check if user has active tasks
        if user.role == 'driver' and user.driver_profile:
            from models import Task
            active_tasks = Task.query.filter_by(driver_id=user.driver_profile.id, status='in_progress').count()
            if active_tasks > 0:
                return jsonify({'error': 'Cannot delete user with active tasks'}), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500