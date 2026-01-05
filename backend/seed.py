import random
from faker import Faker
from sqlalchemy.orm import Session
from seederdb import SessionLocal
from models.user import User
from models.places import Place
from models.reviews import Review

fake = Faker()

def seed_data(num_users=10, num_places=15, reviews_per_place=5):
    db= SessionLocal()
    try:
        print(f"Seeding {num_users} users...")
        users = []
        for _ in range(num_users):
            # Requirements: User has a name and unique phone number [cite: 13, 14]
            user = User(
                user_name=fake.name(),
                phone_number=fake.unique.phone_number(),
                password="hashed_password_here" # In production, hash this properly
            )
            db.add(user)
            users.append(user)
        db.flush()

        print(f"Seeding {num_places} places...")
        places = []
        for _ in range(num_places):
            # Requirements: Place has a name and address [cite: 16]
            place = Place(
                name=fake.company(),
                address=fake.address()
            )
            db.add(place)
            places.append(place)
        db.flush()

        print(f"Seeding reviews...")
        for place in places:
            # Requirements: Random amount of reviews per place 
            for _ in range(random.randint(1, reviews_per_place)):
                user = random.choice(users)
                # Requirements: 1-5 rating and text 
                review = Review(
                    rating=random.randint(1, 5),
                    text=fake.paragraph(nb_sentences=3),
                    user_id=user.id,
                    place_id=place.id
                )
                db.add(review)

        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()