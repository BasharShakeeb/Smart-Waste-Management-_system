import math
from flask import Blueprint, request, jsonify, session
from models import db, Task, TaskBin, Bin, Driver, User

optimize_api = Blueprint('optimize_api', __name__)


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two GPS coordinates."""
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


def greedy_nearest_neighbor(bins, start_lat, start_lng):
    """Sort bins by nearest-neighbor heuristic starting from driver location."""
    unvisited = list(bins)
    route = []
    total_km = 0.0
    current = (start_lat, start_lng)

    while unvisited:
        nearest = min(
            unvisited,
            key=lambda b: haversine(current[0], current[1],
                                    b['latitude'] or 0, b['longitude'] or 0)
        )
        dist = haversine(current[0], current[1],
                         nearest['latitude'] or 0, nearest['longitude'] or 0)
        total_km += dist
        nearest['distance_from_prev'] = round(dist, 2)
        route.append(nearest)
        current = (nearest['latitude'] or 0, nearest['longitude'] or 0)
        unvisited.remove(nearest)

    return route, round(total_km, 2)


@optimize_api.route('/api/tasks/<int:task_id>/optimize-route', methods=['POST'])
def optimize_task_route(task_id):
    """
    Optimize collection route for a task using Greedy Nearest Neighbor.
    Expects JSON: { "driver_lat": float, "driver_lng": float }
    Updates sequence_order in TaskBin records.
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    task = Task.query.get_or_404(task_id)

    # Permission check
    if session.get('role') == 'driver':
        user = User.query.get(session['user_id'])
        if not user or not user.driver_profile:
            return jsonify({'error': 'Driver profile not found'}), 404
        if task.driver_id != user.driver_profile.id:
            return jsonify({'error': 'Access denied'}), 403

    data = request.get_json() or {}
    driver_lat = data.get('driver_lat')
    driver_lng = data.get('driver_lng')

    # Fallback: use driver's stored location
    if driver_lat is None or driver_lng is None:
        if session.get('role') == 'driver':
            user = User.query.get(session['user_id'])
            drv = user.driver_profile if user else None
            if drv and drv.current_location_lat:
                driver_lat = drv.current_location_lat
                driver_lng = drv.current_location_lng

    # Hard fallback to center of Riyadh
    if driver_lat is None:
        driver_lat, driver_lng = 24.6262, 46.5631

    # Collect bins with coordinates
    task_bins = TaskBin.query.filter_by(task_id=task_id).all()
    bins_data = []
    for tb in task_bins:
        b = tb.bin
        if b and b.latitude and b.longitude:
            bins_data.append({
                'task_bin_id': tb.id,
                'bin_id': b.id,
                'bin_identifier': b.bin_id,
                'location': b.location,
                'latitude': b.latitude,
                'longitude': b.longitude,
                'fill_level': b.fill_level,
                'status': tb.status,
            })

    if not bins_data:
        return jsonify({'error': 'No bins with coordinates found for this task'}), 400

    # Run optimization
    optimized_route, total_km = greedy_nearest_neighbor(
        bins_data, driver_lat, driver_lng
    )

    # Estimated time: avg 15 km/h in city + 5 min per bin collection
    avg_speed_kmh = 15
    travel_time_min = (total_km / avg_speed_kmh) * 60
    collection_time_min = len(optimized_route) * 5
    total_time_min = round(travel_time_min + collection_time_min)

    # Persist sequence_order to DB
    for idx, item in enumerate(optimized_route):
        tb = TaskBin.query.get(item['task_bin_id'])
        if tb:
            tb.sequence_order = idx + 1
    db.session.commit()

    # Update task estimated fields
    task.estimated_distance = total_km
    task.estimated_duration = total_time_min
    db.session.commit()

    return jsonify({
        'message': 'Route optimized successfully',
        'driver_start': {'lat': driver_lat, 'lng': driver_lng},
        'optimized_route': optimized_route,
        'total_distance_km': total_km,
        'estimated_duration_min': total_time_min,
        'bins_count': len(optimized_route)
    })


@optimize_api.route('/api/tasks/<int:task_id>/bins-ordered', methods=['GET'])
def get_ordered_bins(task_id):
    """Return task bins sorted by sequence_order with full details."""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401

    task = Task.query.get_or_404(task_id)

    task_bins = (TaskBin.query
                 .filter_by(task_id=task_id)
                 .order_by(TaskBin.sequence_order.asc().nullslast())
                 .all())

    result = []
    for tb in task_bins:
        b = tb.bin
        result.append({
            'task_bin_id': tb.id,
            'sequence_order': tb.sequence_order,
            'bin_id': b.id if b else None,
            'bin_identifier': b.bin_id if b else None,
            'location': b.location if b else None,
            'latitude': b.latitude if b else None,
            'longitude': b.longitude if b else None,
            'fill_level': b.fill_level if b else None,
            'status': tb.status,
            'collected_time': tb.collected_time.isoformat() if tb.collected_time else None,
        })

    return jsonify({
        'task_id': task_id,
        'bins': result,
        'total_distance_km': task.estimated_distance,
        'estimated_duration_min': task.estimated_duration,
    })
