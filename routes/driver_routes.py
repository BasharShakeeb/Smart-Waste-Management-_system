from operator import contains
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from models import db, User, Task, Driver
from utils import admin_required

driver_api = Blueprint('driver_api', __name__)

# Drivers API
@driver_api.route('/api/drivers', methods=['GET'])
@admin_required
def api_get_drivers():
    try:
        
       
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        search = request.args.get('search')
        
        query = Driver.query.join(User).filter(User.is_active == True)
        
        if status:
            query = query.filter(Driver.status == status)
        
        if search:
            query = query.filter(
                db.or_(
                    User.name.contains(search),
                    User.email.contains(search),
                    Driver.license_number.contains(search)
                )
            )
        
        query = query.order_by(Driver.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        drivers = [driver.to_dict() for driver in pagination.items]
        
        return jsonify({
            'drivers': drivers,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@driver_api.route('/api/drivers/<int:driver_id>', methods=['GET'])
@admin_required
def api_get_driver(driver_id):
    try:
        driver = Driver.query.get_or_404(driver_id)
      
        driver_data = driver.to_dict()
        
        
        # Add user information
        if driver.user:
            driver_data.update({
                'name': driver.user.name,
                'email': driver.user.email,
                'phone': driver.user.phone,
                'username': driver.user.username,
                'is_active': driver.user.is_active
            })
        
        # Add task statistics
        total_tasks = Task.query.filter_by(driver_id=driver.id).count()
        completed_tasks = Task.query.filter_by(driver_id=driver.id, status='completed').count()
        active_tasks = Task.query.filter_by(driver_id=driver.id, status='in_progress').count()
        
        driver_data.update({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'active_tasks': active_tasks
        })
        
        return jsonify({'driver': driver_data})
    except Exception as e:
        
        return jsonify({'error': str(e)}), 500

@driver_api.route('/api/drivers/<int:driver_id>', methods=['PUT'])
@admin_required
def api_update_driver(driver_id):
    
    try:
       
        driver = Driver.query.get_or_404(driver_id)
        
        data = request.get_json()
       
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        
            
        # Update driver fields
        for field in ['license_number', 'license_expiry', 'vehicle_id', 'emergency_contact', 'emergency_phone', 'status', 'vehicle_type']:
            if field in data:
                if field == 'license_expiry' and data[field]:
                    setattr(driver, field, datetime.fromisoformat(data[field]).date())
                else:
                    setattr(driver, field, data[field])
        
        # Update user fields if provided
        if driver.user:
            user = driver.user
            for field in ['name', 'email', 'phone', 'username']:
                
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
            
            user.updated_at = datetime.utcnow()
        
        driver.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Driver updated successfully', 'driver': driver.to_dict()})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# @driver_api.route('/api/drivers/<int:driver_id>', methods=['PUT'])
# @admin_required
# def api_update_driver(driver_id):
        
#     try:
#         driver = Driver.query.get_or_404(driver_id)
        
#         data = request.get_json()
#         print(f"Data: {data}")
#         if not data:
#             return jsonify({'error': 'JSON data required'}), 400
        
#         # تحديث حقول السائق
#         for field in ['license_number', 'license_expiry', 'vehicle_id', 'emergency_contact', 'emergency_phone', 'status']:
#             if field in data:
#                 if field == 'license_expiry' and data[field]:
#                     setattr(driver, field, datetime.fromisoformat(data[field]).date())
                
#                 elif field == 'vehicle_id':
#                     val = data[field]
#                     # حالة الحقل فارغ -> NULL
#                     if val == '' or val is None:
#                         driver.vehicle_id = None
#                     else:
#                         driver.vehicle_id = int(val)
#                         # حاول تحويل القيمة إلى int (id)
#                         try:
#                             vehicle_id_int = int(val)
#                             vehicle = Vehicle.query.get(vehicle_id_int)
#                             if not vehicle:
#                                 return jsonify({'error': f'Vehicle with id {vehicle_id_int} not found'}), 400
#                             driver.vehicle_id = vehicle_id_int
#                         except (ValueError, TypeError):
#                             # القيمة ليست رقمًا -> حاول البحث بحسب license_plate
#                             # نستخدم no_autoflush لتجنّب flush مبكر إذا كان هناك تغييرات معلقة
#                             with db.session.no_autoflush:
#                                 vehicle = Vehicle.query.filter(Vehicle.license_plate == val).first()
#                             if vehicle:
#                                 driver.vehicle_id = vehicle.id
#                             else:
#                                 return jsonify({'error': f'Invalid vehicle identifier: {val}'}), 400
#                 else:
#                     setattr(driver, field, data[field])
        
#         # تحديث حقول المستخدم إذا وجدت
#         if driver.user:
#             user = driver.user
#             for field in ['name', 'email', 'phone', 'username']:
#                 if field in data:
#                     if field == 'email' and data[field] != user.email:
#                         if User.query.filter_by(email=data[field]).first():
#                             return jsonify({'error': 'Email already exists'}), 400
                    
#                     if field == 'username' and data[field] != user.username:
#                         if User.query.filter_by(username=data[field]).first():
#                             return jsonify({'error': 'Username already exists'}), 400
                    
#                     setattr(user, field, data[field])
            
#             if 'password' in data:
#                 user.set_password(data['password'])
            
#             user.updated_at = datetime.utcnow()
        
#         driver.updated_at = datetime.utcnow()
#         db.session.commit()
        
#         return jsonify({'message': 'Driver updated successfully', 'driver': driver.to_dict()})
#     except ValueError as e:
#         return jsonify({'error': str(e)}), 400
#     except Exception as e:
#         # طباعة استثناء في السرفر مفيد للتديباغ
#         print("Exception in api_update_driver:", repr(e))
#         return jsonify({'error': str(e)}), 500

@driver_api.route('/api/drivers/<int:driver_id>', methods=['DELETE'])
@admin_required
def api_delete_driver(driver_id):
    
    try:
        driver = Driver.query.get_or_404(driver_id)
        
        # Check if driver has active tasks
        active_tasks = Task.query.filter_by(driver_id=driver.id, status='in_progress').count()
        if active_tasks > 0:
            return jsonify({'error': 'Cannot delete driver with active tasks'}), 400
        
        # Get the associated user
        user = driver.user
        
        # Delete driver profile first (due to foreign key constraints)
        db.session.delete(driver)
        
        # Delete the user as well if requested
        if user:
            db.session.delete(user)
        
        db.session.commit()
        
        return jsonify({'message': 'Driver deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500




