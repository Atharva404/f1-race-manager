from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Driver(db.Model):
    __tablename__ = 'drivers'
    driver_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    country = db.Column(db.String(100))

    def __repr__(self):
        return f"<Driver {self.driver_id}: {self.name}>"


class Team(db.Model):
    __tablename__ = 'teams'
    team_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


class Circuit(db.Model):
    __tablename__ = 'circuits'
    circuit_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))


class Race(db.Model):
    __tablename__ = 'races'
    race_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'))
    circuit_id = db.Column(db.Integer, db.ForeignKey('circuits.circuit_id'))

    team = db.relationship('Team', backref=db.backref('races', lazy=True))
    circuit = db.relationship('Circuit', backref=db.backref('races', lazy=True))

    def __repr__(self):
        return f"<Race {self.race_id}: {self.title} @ {self.start_time}>"


class RaceDriver(db.Model):
    __tablename__ = 'race_drivers'
    race_id = db.Column(db.Integer, db.ForeignKey('races.race_id'), primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.driver_id'), primary_key=True)

    race = db.relationship('Race', backref=db.backref('drivers', cascade="all, delete-orphan"))
    driver = db.relationship('Driver')
