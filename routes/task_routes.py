from flask import Blueprint, request, jsonify, session
from datetime import datetime
from models import db, Task, Driver, Vehicle, User, Bin, TaskBin
from utils import admin_required, driver_required, validate_json_data
import json

task_api = Blueprint('task_api', __name__)

# Tasks API
@task_api.route('/api/tasks', methods=['GET'])
@driver_required
def api_get_tasks():
    try:
        print("\n🔍 Dashboard query triggered")
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        driver_id = request.args.get('driver_id', type=int)
        priority = request.args.get('priority')
        
        query = Task.query
        
        # If user is driver, only show their tasks
        if session.get('role') == 'driver':
            user = User.query.get(session['user_id'])
            if user.driver_profile:
                query = query.filter(Task.driver_id == user.driver_profile.id)
        elif driver_id:
            query = query.filter(Task.driver_id == driver_id)
        
        if status:
            query = query.filter(Task.status == status)
        
        if priority:
            query = query.filter(Task.priority == priority)
        
        query = query.order_by(Task.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        tasks = [task.to_dict() for task in pagination.items]
        
        return jsonify({
            'tasks': tasks,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@task_api.route('/api/tasks', methods=['POST'])
@admin_required
# @validate_json_data(['driver_id', 'vehicle_id', 'bin_ids'])
def api_create_task():
    try:
        data = request.get_json()
        print(data.keys())
        print(data.values())
        print(data["driver_id"], "vehicle_id", data["vehicle_id"])
        
        # Validate driver and vehicle exist
        driver = Driver.query.get(data['driver_id'])
        if not driver:
            return jsonify({'error': 'Driver not found'}), 404
        
        # Check if vehicle_id is valid
        vehicle_id = data['vehicle_id']
        if not vehicle_id or vehicle_id == 'None' or vehicle_id == '':
            return jsonify({'error': 'No vehicle assigned to this driver. Please assign a vehicle to the driver first.'}), 400
        
        # vehicle = Vehicle.query.get(vehicle_id)
        # if not vehicle:
        #     return jsonify({'error': 'Vehicle not found'}), 404
        
        # if vehicle.status != 'available':
        #     return jsonify({'error': 'Vehicle not available'}), 400
        
        # Create task
        task = Task(
            task_id=f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            title=data.get('title', f'Collection Task - {datetime.now().strftime("%Y-%m-%d")}'),
            description=data.get('description'),
            driver_id=data['driver_id'],
            vehicle_id=data['vehicle_id'],
            created_by=session['user_id'],
            route_name=data.get('route_name'),
            estimated_duration=data.get('estimated_duration'),
            priority=data.get('priority', 'normal'),
            status='assigned',  # Set status to assigned when created
            scheduled_time=datetime.fromisoformat(data['scheduled_time']) if data.get('scheduled_time') else None
        )
        
        db.session.add(task)
        db.session.flush()  # Get task ID
        
        # # Add bins to task
        # for i, bin_id in enumerate(data['bin_ids']):
        #     bin_obj = Bin.query.get(bin_id)
        #     if not bin_obj:
        #         return jsonify({'error': f'Bin {bin_id} not found'}), 404
            
        #     task_bin = TaskBin(
        #         task_id=task.id,
        #         bin_id=bin_id,
        #         sequence_order=i + 1,
        #         fill_level_before=bin_obj.fill_level
        #     )
        #     db.session.add(task_bin)
            

        # بعد data = request.get_json()
        bins_raw = data.get('bin_ids')

        # Normalize to a Python list of ids
        bins_list = []
        if bins_raw is None:
            return jsonify({'error': 'bin_ids is required'}), 400

        # Case: a real list already (good)
        if isinstance(bins_raw, list):
            bins_list = bins_raw
        elif isinstance(bins_raw, str):
            # Try to parse JSON string like '["1","2"]'
            try:
                parsed = json.loads(bins_raw)
                if isinstance(parsed, list):
                    bins_list = parsed
                else:
                    # maybe a comma separated string "1,2,3"
                    bins_list = [x.strip() for x in bins_raw.split(',') if x.strip() != ""]
            except json.JSONDecodeError:
                # fallback: "1,2" style
                bins_list = [x.strip() for x in bins_raw.split(',') if x.strip() != ""]
        else:
            return jsonify({'error': 'Invalid bin_ids format'}), 400

        # convert to ints and validate
        clean_bin_ids = []
        for b in bins_list:
            try:
                bid = int(b)
                clean_bin_ids.append(bid)
            except (ValueError, TypeError):
                return jsonify({'error': f'Invalid bin id: {b}'}), 400

        # Now iterate using clean_bin_ids
        for i, bin_id in enumerate(clean_bin_ids):
            bin_obj = Bin.query.get(bin_id)
            if not bin_obj:
                return jsonify({'error': f'Bin {bin_id} not found'}), 404

            task_bin = TaskBin(
                task_id=task.id,
                bin_id=bin_id,
                sequence_order=i + 1,
                fill_level_before=bin_obj.fill_level
            )
            db.session.add(task_bin)

        # Update vehicle status
        # vehicle.status = 'in_use'
        
            db.session.commit()
        
        return jsonify({'message': 'Task created successfully', 'task': task.to_dict()}), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@task_api.route('/api/tasks/<int:task_id>', methods=['GET'])
@driver_required
def api_get_task(task_id):
    try:
        
        task = Task.query.get_or_404(task_id)
        # Check permission
        if session.get('role') == 'driver':
            user = User.query.get(session['user_id'])
            if user.driver_profile and task.driver_id != user.driver_profile.id:
                return jsonify({'error': 'Access denied'}), 403
        
        task_data = task.to_dict()
        task_data['bins'] = [tb.to_dict() for tb in task.task_bins]
        
        return jsonify({'task': task_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@task_api.route('/api/tasks/<int:task_id>', methods=['PUT'])
@driver_required
def api_update_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Check permission
        if session.get('role') == 'driver':
            user = User.query.get(session['user_id'])
            if user.driver_profile and task.driver_id != user.driver_profile.id:
                return jsonify({'error': 'Access denied'}), 403
            
            # Drivers can only update certain fields
            allowed_fields = ['status', 'started_time', 'completed_time', 'notes', 'actual_duration', 'actual_distance']
            data = {k: v for k, v in data.items() if k in allowed_fields}
        
        # Update task fields
        for field in ['title', 'description', 'status', 'priority', 'scheduled_time', 'started_time', 'completed_time', 'notes', 'actual_duration', 'actual_distance']:
            if field in data:
                if field in ['scheduled_time', 'started_time', 'completed_time'] and data[field]:
                    setattr(task, field, datetime.fromisoformat(data[field]))
                else:
                    setattr(task, field, data[field])
        
        # Update vehicle status based on task status
        if 'status' in data:
            if data['status'] == 'completed':
                # task.vehicle.status = 'available'
                task.completed_time = datetime.utcnow()
            elif data['status'] == 'in_progress':
                task.started_time = datetime.utcnow()
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Task updated successfully', 'task': task.to_dict()})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@task_api.route('/api/tasks/<int:task_id>/bins/<int:bin_id>', methods=['PUT'])
@driver_required
def api_update_task_bin(task_id, bin_id):
    try:
        task_bin = TaskBin.query.filter_by(task_id=task_id, bin_id=bin_id).first_or_404()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Check permission
        if session.get('role') == 'driver':
            user = User.query.get(session['user_id'])
            if user.driver_profile and task_bin.task.driver_id != user.driver_profile.id:
                return jsonify({'error': 'Access denied'}), 403
        
        # Update task bin
        for field in ['status', 'collected_time', 'fill_level_after', 'weight_collected', 'notes', 'photo_url']:
            if field in data:
                if field == 'collected_time' and data[field]:
                    setattr(task_bin, field, datetime.fromisoformat(data[field]))
                else:
                    setattr(task_bin, field, data[field])
        
        # If marked as collected, update bin
        if data.get('status') == 'collected':
            task_bin.collected_time = datetime.utcnow()
            task_bin.bin.last_collected = datetime.utcnow()
            task_bin.bin.fill_level = data.get('fill_level_after', 0)
        
        task_bin.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Task bin updated successfully', 'task_bin': task_bin.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500