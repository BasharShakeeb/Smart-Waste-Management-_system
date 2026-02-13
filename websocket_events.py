from flask_socketio import emit, join_room, leave_room
from flask import session
from datetime import datetime
from models import Bin, Driver, User

def init_socketio_events(socketio):
    """Initialize all WebSocket events"""
    
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        if 'user_id' in session:
            join_room(f"user_{session['user_id']}")
            join_room(session['role'])  # Join role-based room
            emit('status', {'msg': f"{session['name']} connected"})

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
        if 'user_id' in session:
            leave_room(f"user_{session['user_id']}")
            leave_room(session['role'])

    @socketio.on('join_dashboard')
    def handle_join_dashboard():
        join_room('dashboard')
        emit('dashboard_joined', {'status': 'success'})

    @socketio.on('join_bins')
    def handle_join_bins():
        join_room('bins')
        emit('bins_joined', {'status': 'success'})

    @socketio.on('join_drivers')
    def handle_join_drivers():
        join_room('drivers')
        emit('drivers_joined', {'status': 'success'})

    @socketio.on('request_bin_data')
    def handle_bin_data_request():
        bins = Bin.query.all()
        bins_data = [bin.to_dict() for bin in bins]
        emit('bin_data_update', {'bins': bins_data})

    @socketio.on('request_dashboard_stats')
    def handle_dashboard_stats_request():
        total_bins = Bin.query.count()
        full_bins = Bin.query.filter(Bin.fill_level >= 80).count()
        active_bins = Bin.query.filter(Bin.status == 'active').count()
        active_drivers = Driver.query.filter(Driver.status == 'online').count()
        
        emit('dashboard_stats_update', {
            'total_bins': total_bins,
            'full_bins': full_bins,
            'active_bins': active_bins,
            'active_drivers': active_drivers,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })