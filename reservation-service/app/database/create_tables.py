from app.database.database import Base, engine
from app.models.reservation import Reservation
from app.models.user import User

Base.metadata.create_all(bind=engine)

print("Tablas creadas")
