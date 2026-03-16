from database import SessionLocal, User
import json

db = SessionLocal()
try:
    user = db.query(User).filter(User.email == "abhi@gmail.com").first()
    if user:
        print(f"User found: ID={user.id}, Name='{user.name}', Email='{user.email}'")
    else:
        print("User 'abhi@gmail.com' not found.")
    
    all_users = db.query(User).all()
    print("\nAll users in DB:")
    for u in all_users:
        print(f"- {u.email}: {u.name}")
finally:
    db.close()
