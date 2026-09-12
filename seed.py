from app import create_app, db
from app.models import Seat

app = create_app()

def seed_seats():
    with app.app_context():
        db.create_all()
        
        # Check if already seeded
        if Seat.query.first():
            print("Database already seeded.")
            return

        print("Seeding database...")
        
        # Floor 1
        # 30 individual cubicles
        for i in range(1, 31):
            db.session.add(Seat(floor=1, type='cubicle', label=f'CUB-{i}'))
            
        # 10 circular tables * 8 chairs
        for t in range(1, 11):
            for c in range(1, 9):
                db.session.add(Seat(floor=1, type='circular', label=f'CIR-T{t}-S{c}'))
                
        # 30 rectangular tables * 4 chairs
        for t in range(1, 31):
            for c in range(1, 5):
                db.session.add(Seat(floor=1, type='rectangular', label=f'REC-T{t}-S{c}'))

        # Floor 2 & 3
        for floor in [2, 3]:
            # 15 individual cubicles
            for i in range(1, 16):
                db.session.add(Seat(floor=floor, type='cubicle', label=f'CUB-{i}'))
                
            # 2 circular tables * 8 chairs
            for t in range(1, 3):
                for c in range(1, 9):
                    db.session.add(Seat(floor=floor, type='circular', label=f'CIR-T{t}-S{c}'))
                    
            # 15 rectangular tables * 4 chairs
            for t in range(1, 16):
                for c in range(1, 5):
                    db.session.add(Seat(floor=floor, type='rectangular', label=f'REC-T{t}-S{c}'))
                    
        db.session.commit()
        print("Seeding completed.")

if __name__ == '__main__':
    seed_seats()
