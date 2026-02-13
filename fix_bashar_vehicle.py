#!/usr/bin/env python3
"""
Quick fix to assign a vehicle to Bashar
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Driver, Vehicle

def fix_bashar_vehicle():
    with app.app_context():
        print("🔧 Fixing Bashar's vehicle assignment...")
        
        # Find Bashar
        bashar_user = User.query.filter_by(email='wwee107154@gmail.com').first()
        if not bashar_user or not bashar_user.driver_profile:
            print("❌ Bashar user or driver profile not found!")
            return
        
        bashar_driver = bashar_user.driver_profile
        
        # Find an available vehicle
        available_vehicle = Vehicle.query.filter_by(status='available').first()
        if not available_vehicle:
            print("❌ No available vehicles found!")
            return
        
        # Assign vehicle to Bashar
        bashar_driver.vehicle_id = available_vehicle.id
        db.session.commit()
        
        print(f"✅ Assigned vehicle {available_vehicle.vehicle_id} to Bashar")
        print(f"   Bashar's driver ID: {bashar_driver.id}")
        print(f"   Vehicle ID: {available_vehicle.id}")

if __name__ == '__main__':
    fix_bashar_vehicle()