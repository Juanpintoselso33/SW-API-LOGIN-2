from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY, ForeignKey, Integer
from sqlalchemy.orm import relationship


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id_user = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String)
    password = db.Column(db.String)  
    favourites = db.relationship('Favourite', back_populates='user')
    
    def __repr__(self):
        return f'<User {self.id_user}>'    

    def serialize(self):
        return {
            "id": self.id_user,
            "name": self.name,
            #"favourites": [favourite.serialize() for favourite in self.favourites]
        }


class Favourite(db.Model):
    __tablename__ = 'favourite'
    
    id_favourite = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, ForeignKey('user.id_user'))
    favourite_planet = db.Column(db.Integer, ForeignKey('planet.id'), default=None)
    favourite_person = db.Column(db.Integer, ForeignKey('person.id'), default=None)
    favourite_film = db.Column(db.Integer, ForeignKey('film.id'), default=None)
    favourite_starship = db.Column(db.Integer, ForeignKey('starship.id'), default=None)
    favourite_vehicle = db.Column(db.Integer, ForeignKey('vehicle.id'), default=None)

    # Relaciones
    user = relationship('User', back_populates='favourites')
    planet = relationship('Planet')  # Asumiendo que el modelo Planet tiene un campo id_planet
    person = relationship('Person')  # Asumiendo que el modelo Person tiene un campo id_person
    film = relationship('Film')      # Asumiendo que el modelo Film tiene un campo id_film
    starship = relationship('Starship') # Asumiendo que el modelo Starship tiene un campo id_starship
    vehicle = relationship('Vehicle')   # Asumiendo que el modelo Vehicle tiene un campo id_vehicle

    def __repr__(self):
        return f'<Favourite {self.id_favourite}>'

    def serialize(self):
        return {            
            "id_favourite": self.id_favourite,  
            "id_user": self.id_user,
            "favourite_person": self.favourite_person,          
            "favourite_planet": self.favourite_planet,
            "favourite_starship": self.favourite_starship,          
            "favourite_vehicle": self.favourite_vehicle,
            "favourite_film": self.favourite_film
        }
    
class Person(db.Model):
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    height = db.Column(db.Integer)
    mass = db.Column(db.Integer)
    hair_color = db.Column(db.String)
    skin_color = db.Column(db.String)
    eye_color = db.Column(db.String)
    birth_year = db.Column(db.String)
    gender = db.Column(db.String)
    homeworld = db.Column(db.String)
    url = db.Column(db.String)
    description = db.Column(db.String)

    def __repr__(self):
        return f'<Person {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "homeworld": self.homeworld,
            "url": self.url,
            "description": self.description
        }
    
class Planet(db.Model):
    __tablename__ = 'planet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    diameter = db.Column(db.Integer)
    rotation_period = db.Column(db.Integer)
    orbital_period = db.Column(db.Integer)
    gravity = db.Column(db.String)
    population = db.Column(db.Integer)
    climate = db.Column(db.String)
    terrain = db.Column(db.String)
    surface_water = db.Column(db.Integer)
    url = db.Column(db.String)
    description = db.Column(db.String)

    def __repr__(self):
        return f'<Planet {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "gravity": self.gravity,
            "population": self.population,
            "climate": self.climate,
            "terrain": self.terrain,
            "surface_water": self.surface_water,
            "url": self.url,
            "description": self.description
        }
    
class Film(db.Model):
    __tablename__ = 'film'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    episode_id = db.Column(db.Integer)
    director = db.Column(db.String)
    producer = db.Column(db.String)
    release_date = db.Column(db.String)
    opening_crawl = db.Column(db.String)
    url = db.Column(db.String)
    description = db.Column(db.String)

    def __repr__(self):
        return f'<Film {self.title}>'

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "episode_id": self.episode_id,
            "director": self.director,
            "producer": self.producer,
            "release_date": self.release_date,
            "opening_crawl": self.opening_crawl,
            "url": self.url,
            "description": self.description
        }

class Starship(db.Model):
    __tablename__ = 'starship'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    model = db.Column(db.String)
    starship_class = db.Column(db.String)
    manufacturer = db.Column(db.String)
    cost_in_credits = db.Column(db.Integer)
    length = db.Column(db.Integer)
    crew = db.Column(db.String)
    passengers = db.Column(db.String)
    max_atmosphering_speed = db.Column(db.String)
    hyperdrive_rating = db.Column(db.String)
    MGLT = db.Column(db.Integer)
    cargo_capacity = db.Column(db.Integer)
    consumables = db.Column(db.String)
    url = db.Column(db.String)
    description = db.Column(db.String)

    def __repr__(self):
        return f'<Starship {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "starship_class": self.starship_class,
            "manufacturer": self.manufacturer,
            "cost_in_credits": self.cost_in_credits,
            "length": self.length,
            "crew": self.crew,
            "passengers": self.passengers,
            "max_atmosphering_speed": self.max_atmosphering_speed,
            "hyperdrive_rating": self.hyperdrive_rating,
            "MGLT": self.MGLT,
            "cargo_capacity": self.cargo_capacity,
            "consumables": self.consumables,
            "url": self.url,
            "description": self.description
        }

class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    model = db.Column(db.String)
    vehicle_class = db.Column(db.String)
    manufacturer = db.Column(db.String)
    cost_in_credits = db.Column(db.Integer)
    length = db.Column(db.String)
    crew = db.Column(db.String)
    passengers = db.Column(db.String)
    max_atmosphering_speed = db.Column(db.String)
    cargo_capacity = db.Column(db.Integer)
    consumables = db.Column(db.String)
    url = db.Column(db.String)
    description = db.Column(db.String)

    def __repr__(self):
        return f'<Vehicle {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "vehicle_class": self.vehicle_class,
            "manufacturer": self.manufacturer,
            "cost_in_credits": self.cost_in_credits,
            "length": self.length,
            "crew": self.crew,
            "passengers": self.passengers,
            "max_atmosphering_speed": self.max_atmosphering_speed,
            "cargo_capacity": self.cargo_capacity,
            "consumables": self.consumables,
            "url": self.url,
            "description": self.description
        }