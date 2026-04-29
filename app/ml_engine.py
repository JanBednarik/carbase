from sqlmodel import Session, select

from app.models.used_car import UsedCar


# TODO implemented real recommendation engine
def recommend(session: Session) -> list[UsedCar]:
    return session.exec(select(UsedCar).limit(3)).all()
