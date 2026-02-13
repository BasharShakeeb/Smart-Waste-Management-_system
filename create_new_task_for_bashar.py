#!/usr/bin/env python3
"""
Create a new test task for Bashar Shakeeb to verify driver interface functionality
"""

from app import app, db, User, Driver, Task, Bin, TaskBin
from datetime import datetime, timedelta

def create_test_task():
    with app.app_context():
        # Find Bashar
        bashar = User.query.filter_by(name='Bashar Shakeeb').first()
        if not bashar:
            print("❌ Bashar Shakeeb user not found!")
            return
            
        if not bashar.driver_profile:
            print("❌ Bashar doesn't have a driver profile!")
            return
            
        print(f"✅ Found driver: {bashar.name} (ID: {bashar.driver_profile.id})")
        
        # Get some bins to assign
        bins = Bin.query.filter(Bin.status == 'active').limit(3).all()
        if not bins:
            print("❌ No active bins found!")
            return
            
        print(f"✅ Found {len(bins)} bins to assign")
        
        # Create a new task with 'assigned' status
        task_id = f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        new_task = Task(
            task_id=task_id,
            driver_id=bashar.driver_profile.id,
            vehicle_id=bashar.driver_profile.vehicle_id,  # Use Bashar's assigned vehicle
            description=f"New test collection task for Bashar - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            status='assigned',  # This is the key - set to 'assigned' so it shows up
            priority='normal',
            estimated_duration=45,  # 45 minutes
            scheduled_time=datetime.now() + timedelta(minutes=5),  # Schedule for 5 minutes from now
            created_by=1  # Assuming admin user ID is 1
        )
        
        try:
            db.session.add(new_task)
            db.session.flush()  # Get the task ID
            
            # Add bins to the task
            for i, bin_item in enumerate(bins):
                task_bin = TaskBin(
                    task_id=new_task.id,
                    bin_id=bin_item.id,
                    sequence_order=i + 1,
                    status='pending'
                )
                db.session.add(task_bin)
            
            db.session.commit()
            
            print(f"✅ Created new task: {task_id}")
            print(f"   Status: {new_task.status}")
            print(f"   Priority: {new_task.priority}")
            print(f"   Scheduled: {new_task.scheduled_time}")
            print(f"   Bins assigned: {len(bins)}")
            
            # Verify the task can be queried by the driver dashboard logic
            driver_tasks = Task.query.filter_by(
                driver_id=bashar.driver_profile.id
            ).filter(
                Task.status.in_(['pending', 'assigned', 'in_progress'])
            ).all()
            
            print(f"\n📊 Dashboard query results:")
            print(f"   Tasks visible to Bashar: {len(driver_tasks)}")
            for task in driver_tasks:
                print(f"   - {task.id}: {task.status} - {task.description}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating task: {e}")

if __name__ == "__main__":
    create_test_task()