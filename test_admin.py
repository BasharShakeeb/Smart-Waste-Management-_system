#!/usr/bin/env python3
"""
Test script to check and fix admin user login issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User
from werkzeug.security import generate_password_hash, check_password_hash

def test_admin_user():
    with app.app_context():
        print("🔍 Testing admin user...")
        
        # Try to find admin user
        admin_user = User.query.filter_by(email='admin@collectme.com').first()
        
        if admin_user:
            print(f"✅ Admin user found:")
            print(f"   Email: {admin_user.email}")
            print(f"   Username: {admin_user.username}")
            print(f"   Role: {admin_user.role}")
            print(f"   Active: {admin_user.is_active}")
            print(f"   Password Hash: {admin_user.password_hash[:20]}...")
            
            # Test password
            password_test = admin_user.check_password('admin123')
            print(f"   Password 'admin123' works: {password_test}")
            
            if not password_test:
                print("🔧 Fixing password...")
                admin_user.set_password('admin123')
                db.session.commit()
                print("✅ Password updated!")
                
                # Test again
                password_test_2 = admin_user.check_password('admin123')
                print(f"   Password 'admin123' works now: {password_test_2}")
                
        else:
            print("❌ Admin user not found! Creating...")
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
            print("✅ Admin user created!")

        # List all users
        print("\n📋 All users in database:")
        all_users = User.query.all()
        for user in all_users:
            print(f"   - {user.email} ({user.role}) - Active: {user.is_active}")

if __name__ == "__main__":
    test_admin_user()