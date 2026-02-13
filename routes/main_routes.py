from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from models import TaskBin, db, User, Bin, Driver, Task, Vehicle

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    if 'user_id' in session:
        if session['role'] == 'manager':
            return redirect(url_for('main.dashboard'))
        else:
            return redirect(url_for('main.driver_dashboard'))
    return redirect(url_for('main.login'))

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        user = User.query.filter_by(email=email, role=role, is_active=True).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['name'] = user.name
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            if role in ['admin']: # we delete the manager role parameter
                return redirect(url_for('main.dashboard'))
            else:
                flash('Login successful', 'success') 
                
                return redirect(url_for('main.driver_dashboard'))
        else:
            flash('Invalid login credentials', 'error')
    
    return render_template('login.html')

@main_routes.route('/logout')
def logout():
    driver_id= session['user_id']
    driver = Driver.query.filter_by(user_id=driver_id).first()
    driver.status = 'offline'
    db.session.commit() 
    session.clear()
    return redirect(url_for('main.login'))

@main_routes.route('/dashboard')
def dashboard():
    """
    Dashboard for managers and admins.
    """
    if 'user_id' not in session or session['role'] not in ['admin', 'manager']:
        return redirect(url_for('main.login'))
    
    # Get statistics using the new models
    total_bins = Bin.query.count()
    full_bins = Bin.query.filter(Bin.fill_level >= 80).count()
    active_bins = Bin.query.filter(Bin.status == 'active').count()
    active_drivers = Driver.query.filter(Driver.status == 'online').count()
    
    # Get recent bins (top 10 by fill level)
    bins = Bin.query.order_by(Bin.fill_level.desc()).limit(10).all()
    
    # Get drivers with user information
    drivers = Driver.query.join(User).filter(User.is_active == True).all()
    
    return render_template('dashboard.html', 
                         total_bins=total_bins,
                         full_bins=full_bins,
                         active_bins=active_bins,
                         active_drivers=active_drivers,
                         bins=bins,
                         drivers=drivers)

@main_routes.route('/bins')
def bins_management():
    if 'user_id' not in session or session['role'] not in ['admin', 'manager']:
        return redirect(url_for('main.login'))
    
    bins = Bin.query.order_by(Bin.created_at.desc()).all() 
    return render_template('bins.html', bins=bins)

@main_routes.route('/drivers')
def drivers_management():
    if 'user_id' not in session or session['role'] not in ['admin', 'manager']:
        return redirect(url_for('main.login'))
    # drivers = User.query.filter(User.role == 'driver').all()
    drivers = Driver.query.join(User).filter(User.is_active == True).all()
    
    return render_template('drivers.html', drivers=drivers)

@main_routes.route('/create-task')
def create_task():
    
    if 'user_id' not in session or session['role'] not in ['admin', 'manager']:
        return redirect(url_for('main.login'))
    
    full_bins = Bin.query.filter(Bin.fill_level >= 80, Bin.status == 'active').all() 
    drivers = Driver.query.join(User).filter(User.is_active == True, Driver.status == 'online').all()
    vehicles = Vehicle.query.filter(Vehicle.status == 'available').all()
    
    return render_template('create_task.html', 
                         full_bins=full_bins,
                         drivers=drivers,
                         vehicles=vehicles)

@main_routes.route('/driver-dashboard')
def driver_dashboard():
    print('driver dashboard')
    if 'user_id' not in session or session['role'] != 'driver':
        return redirect(url_for('main.login'))
    
    # # Redirect drivers to main dashboard since driver-specific dashboard was removed
    # return redirect(url_for('main.dashboard'))
    driver_id= session['user_id']
    driver = Driver.query.filter_by(user_id=driver_id).first()
    driverid = driver.id
    driver.status = 'online'
    driver.last_login = datetime.utcnow()
    db.session.commit() 
    task = Task.query.filter_by(driver_id=driverid).all()
    task = [task.to_dict() for task in task]    
    print(task)
    print(driver_id)

    return render_template('driver_dashboard.html', tasks=task) 

# Reports functionality removed

@main_routes.route('/live-map')
def live_map():
    if 'user_id' not in session or session['role'] not in ['admin', 'manager']:
        return redirect(url_for('main.login'))
    
    # Get all active bins for the map
    bins_query = Bin.query.filter(Bin.status == 'active').all()
    bins = [bin.to_dict() for bin in bins_query]
    
    # Get active drivers with their current locations
    drivers_query = Driver.query.join(User).filter(User.is_active == True, Driver.status == 'online').all()
    drivers = [driver.to_dict() for driver in drivers_query]
    
    return render_template('live_map.html', bins=bins, drivers=drivers)