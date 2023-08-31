"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from admin import setup_admin
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from models import db, User, Person, Planet, Film, Starship, Vehicle, Favourite
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False



db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)


# Handle/serialize errors like a JSON object
from flask import Flask, jsonify
from models import db, User, Person, Planet, Film, Starship, Vehicle, Favourite

# ... (tu código existente)

@app.route('/delete_all', methods=['DELETE'])
def delete_all():
    try:
        # Eliminar todos los registros de cada tabla
        Favourite.query.delete()
        Vehicle.query.delete()
        Starship.query.delete()
        Film.query.delete()
        Planet.query.delete()
        Person.query.delete()
        User.query.delete()
        
        # Confirmar los cambios en la base de datos
        db.session.commit()
        
        return jsonify({"msg": "Todas las tablas han sido vaciadas"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error al eliminar registros", "error": str(e)}), 500

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
    if not users:
        return jsonify({"msg": "No users found"}), 404

    users_list = list(map(lambda user: user.serialize(), users))

    response_body = {
        "msg": "Hello, this is your GET /user response",
        "users": users_list
    }

    return jsonify(response_body), 200


@app.route('/user/<int:id_user>', methods=['GET'])
def get_user_by_id(id_user):
    users = User.query.all()
    users_list = list(map(lambda user: user.serialize(), users))
    filtered_users = list(
        filter(lambda user: user['id'] == id_user, users_list))

    if len(filtered_users) == 0:
        return jsonify({"msg": "User not found"}), 404

    return jsonify(filtered_users[0]), 200


@app.route('/user/<int:id_user>/favourites', methods=['GET'])
def get_user_favourites(id_user):
    user = User.query.get(id_user)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    favourites = user.favourites  # Ahora es una lista de objetos Favourite
    if not favourites:
        return jsonify({"msg": "No favourites found for this user"}), 404

    # Utilizar map para serializar cada objeto Favourite en la lista
    serialized_favourites = list(map(lambda favourite: favourite.serialize(), favourites))
    
    return jsonify(serialized_favourites), 200

@app.route('/favourite', methods=['POST'])
def add_favourite():
    data = request.get_json()

    # Verificar si el JSON contiene todos los campos necesarios
    if not data or 'id_user' not in data:
        return jsonify({"msg": "Missing fields"}), 400

    id_user = data['id_user']

    # Verificar si el usuario existe
    user = User.query.get(id_user)
    if user is None:
        return jsonify({"msg": "User not found"}), 404

    # Crear un diccionario para guardar los valores de los campos favoritos
    favourite_data = {'id_user': id_user}

    for key in ['favourite_planet', 'favourite_person', 'favourite_film', 'favourite_starship', 'favourite_vehicle']:
        if key in data:
            entity_id = data[key]
            entity = None
            entity_type = key.split('_')[1]

            # Verificar si ya existe un favorito para el mismo usuario y la misma entidad
            existing_favourite = Favourite.query.filter_by(id_user=id_user).filter_by(**{key: entity_id}).first()
            if existing_favourite:
                return jsonify({"msg": f"Duplicate favourite for {entity_type}"}), 400

            # Verificar si la entidad favorita existe
            if entity_type == 'planet':
                entity = Planet.query.get(entity_id)
            elif entity_type == 'person':
                entity = Person.query.get(entity_id)
            elif entity_type == 'film':
                entity = Film.query.get(entity_id)
            elif entity_type == 'starship':
                entity = Starship.query.get(entity_id)
            elif entity_type == 'vehicle':
                entity = Vehicle.query.get(entity_id)

            if entity is None:
                return jsonify({"msg": f"{entity_type.capitalize()} not found"}), 404
            
            # Añadir al diccionario
            favourite_data[key] = entity_id

    # Crear la nueva entidad de tipo Favorito
    new_favourite = Favourite(**favourite_data)

    # Añadir la nueva entidad Favorito a la base de datos y hacer commit
    db.session.add(new_favourite)
    db.session.commit()

    return jsonify({"msg": "Favourite added successfully", "id_favourite": new_favourite.id_favourite}), 201

@app.route('/user/<int:id_user>/favourites/<int:id_favourite>', methods=['DELETE'])
def delete_user_favourite(id_user, id_favourite):
    # Verificar si el usuario existe
    user = User.query.get(id_user)
    if user is None:
        return jsonify({"msg": "User not found"}), 404

    # Buscar la entidad Favorito por su ID
    favourite = Favourite.query.get(id_favourite)

    # Si no se encuentra el favorito, devolver un error 404
    if favourite is None:
        return jsonify({"msg": "Favourite not found"}), 404

    # Verificar si el favorito pertenece al usuario
    if favourite.id_user != id_user:
        return jsonify({"msg": "Favourite does not belong to the user"}), 403

    # Eliminar el favorito de la base de datos
    db.session.delete(favourite)
    db.session.commit()

    return jsonify({"msg": "Favourite deleted successfully"}), 200   

@app.route('/person', methods=['GET'])
def get_persons():
    persons = Person.query.all()
    if not persons:
        return jsonify({"msg": "No persons found"}), 404

    person_list = list(map(lambda person: person.serialize(), persons))

    response_body = {
        "msg": "Hello, this is your GET /person response",
        "persons": person_list
    }

    return jsonify(response_body), 200


@app.route('/person/<int:id_person>', methods=['GET'])
def get_person_by_id(id_person):
    persons = Person.query.all()
    person_list = list(map(lambda person: person.serialize(), persons))

    filtered_persons = list(
        filter(lambda person: person['id'] == id_person, person_list))

    if len(filtered_persons) == 0:
        return jsonify({"msg": "Person not found"}), 404

    return jsonify(filtered_persons[0]), 200

@app.route('/person', methods=['POST'])
def create_person():
    data = request.json
    
    existing_person = Person.query.filter_by(name=data['name']).first()
    if existing_person:
        return jsonify({"msg": "Person with the same name already exists"}), 400
    
    person = Person(
        name=data['name'],
        height=data['height'],
        mass=data['mass'],
        hair_color=data['hair_color'],
        skin_color=data['skin_color'],
        eye_color=data['eye_color'],
        birth_year=data['birth_year'],
        gender=data['gender'],
        homeworld=data['homeworld'],
        url=data['url'],
        description=data['description']
    )
    db.session.add(person)
    db.session.commit()
    
    return jsonify({"msg": "Person created successfully"}), 201

@app.route('/person/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    person = Person.query.get(person_id)
    
    if not person:
        return jsonify({"msg": "Person not found"}), 404
    
    users = User.query.all()
    for user in users:
        if user.favourites:
            for favourite in user.favourites:
                if favourite.favourite_person == person_id:
                    db.session.delete(favourite)
                    db.session.commit()
    
    db.session.delete(person)
    db.session.commit()    
    return jsonify({"msg": "Person deleted successfully"}), 200

@app.route('/person/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    person = Person.query.get(person_id)
    
    if not person:
        return jsonify({"msg": "Person not found"}), 404
    
    data = request.get_json()
    person.name = data['name']
    person.height = data['height']
    person.mass = data['mass']
    person.hair_color = data['hair_color']
    person.skin_color = data['skin_color']
    person.eye_color = data['eye_color']
    person.birth_year = data['birth_year']
    person.gender = data['gender']
    person.homeworld = data['homeworld']
    person.url = data['url']
    person.description = data['description']
    
    db.session.commit()
    return jsonify({"msg": "Person updated successfully"}), 200

@app.route('/planet', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    if not planets:
        return jsonify({"msg": "No planets found"}), 404

    planet_list = list(map(lambda planet: planet.serialize(), planets))

    response_body = {
        "msg": "Hello, this is your GET /planet response",
        "planets": planet_list
    }

    return jsonify(response_body), 200


@app.route('/planet/<int:id_planet>', methods=['GET'])
def get_planet_by_id(id_planet):
    planets = Planet.query.all()
    planet_list = list(map(lambda planet: planet.serialize(), planets))
    filtered_planets = list(
        filter(lambda planet: planet['id'] == id_planet, planet_list))

    if len(filtered_planets) == 0:
        return jsonify({"msg": "Planet not found"}), 404

    return jsonify(filtered_planets[0]), 200

@app.route('/planet', methods=['POST'])
def add_planet():
    data = request.get_json()
    required_attributes = ['name', 'diameter', 'rotation_period', 'orbital_period', 'gravity', 'population', 'climate', 'terrain', 'surface_water', 'url', 'description']
    for attribute in required_attributes:
        if attribute not in data:
            return jsonify({"msg": f"Missing {attribute}"}), 400

    existing_planet = Planet.query.filter_by(name=data['name']).first()
    if existing_planet:
        return jsonify({"msg": "Planet with that name already exists"}), 400

    new_planet = Planet(
        name=data['name'],
        diameter=data['diameter'],
        rotation_period=data['rotation_period'],
        orbital_period=data['orbital_period'],
        gravity=data['gravity'],
        population=data['population'],
        climate=data['climate'],
        terrain=data['terrain'],
        surface_water=data['surface_water'],
        url=data['url'],
        description=data['description']
    )
    db.session.add(new_planet)
    db.session.commit()
    return jsonify({"msg": "Planet added successfully"}), 201

@app.route('/planet/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404

    # Buscar todos los favoritos que hacen referencia al planeta
    favourites = Favourite.query.filter_by(favourite_planet=planet_id).all()

    # Eliminar esos favoritos
    for favourite in favourites:
        db.session.delete(favourite)
    
    # Finalmente, eliminar el planeta
    db.session.delete(planet)
    db.session.commit()

    return jsonify({"msg": "Planet and associated favourites deleted successfully"}), 200



@app.route('/planet/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get(planet_id)
    
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404
    
    data = request.json
    
    planet.name = data.get('name', planet.name)
    planet.diameter = data.get('diameter', planet.diameter)
    planet.rotation_period = data.get('rotation_period', planet.rotation_period)
    planet.orbital_period = data.get('orbital_period', planet.orbital_period)
    planet.gravity = data.get('gravity', planet.gravity)
    planet.population = data.get('population', planet.population)
    planet.climate = data.get('climate', planet.climate)
    planet.terrain = data.get('terrain', planet.terrain)
    planet.surface_water = data.get('surface_water', planet.surface_water)
    planet.url = data.get('url', planet.url)
    planet.description = data.get('description', planet.description)
    
    db.session.commit()
    
    return jsonify({"msg": "Planet updated successfully"}), 200


@app.route('/film', methods=['GET'])
def get_films():
    films = Film.query.all()
    if not films:
        return jsonify({"msg": "No films found"}), 404

    film_list = list(map(lambda film: film.serialize(), films))

    response_body = {
        "msg": "Hello, this is your GET /film response",
        "films": film_list
    }

    return jsonify(response_body), 200


@app.route('/film/<int:id_film>', methods=['GET'])
def get_film_by_id(id_film):
    films = Film.query.all()
    film_list = list(map(lambda film: film.serialize(), films))

    filtered_films = list(
        filter(lambda film: film['id'] == id_film, film_list))

    if len(filtered_films) == 0:
        return jsonify({"msg": "Film not found"}), 404

    return jsonify(filtered_films[0]), 200


@app.route('/film', methods=['POST'])
def add_film():
    data = request.get_json()
    required_attributes = ['title', 'episode_id', 'director', 'producer', 'release_date', 'opening_crawl', 'url', 'description']
    for attribute in required_attributes:
        if attribute not in data:
            return jsonify({"msg": f"Missing {attribute}"}), 400

    existing_film = Film.query.filter_by(title=data['title']).first()
    if existing_film:
        return jsonify({"msg": "Film with that title already exists"}), 400

    new_film = Film(
        title=data['title'],
        episode_id=data['episode_id'],
        director=data['director'],
        producer=data['producer'],
        release_date=data['release_date'],
        opening_crawl=data['opening_crawl'],
        url=data['url'],
        description=data['description']
    )
    db.session.add(new_film)
    db.session.commit()
    return jsonify({"msg": "Film added successfully"}), 201

@app.route('/film/<int:film_id>', methods=['DELETE'])
def delete_film(film_id):
    film = Film.query.get(film_id)
    
    if not film:
        return jsonify({"msg": "Film not found"}), 404
    
    users = User.query.all()
    for user in users:
        if user.favourites:
            for favourite in user.favourites:
                if favourite.favourite_film == film_id:
                    db.session.delete(favourite)
                    db.session.commit()
    
    db.session.delete(film)
    db.session.commit()    
    return jsonify({"msg": "Film deleted successfully"}), 200

@app.route('/film/<int:film_id>', methods=['PUT'])
def update_film(film_id):
    film = Film.query.get(film_id)
    
    if not film:
        return jsonify({"msg": "Film not found"}), 404
    
    data = request.json
    
    film.title = data.get('title', film.title)
    film.episode_id = data.get('episode_id', film.episode_id)
    film.director = data.get('director', film.director)
    film.producer = data.get('producer', film.producer)
    film.release_date = data.get('release_date', film.release_date)
    film.opening_crawl = data.get('opening_crawl', film.opening_crawl)
    film.url = data.get('url', film.url)
    film.description = data.get('description', film.description)
    
    db.session.commit()
    
    return jsonify({"msg": "Film updated successfully"}), 200


@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = Vehicle.query.all()
    if not vehicles:
        return jsonify({"msg": "No vehicles found"}), 404
    vehicle_list = list(map(lambda vehicle: vehicle.serialize(), vehicles))

    response_body = {
        "msg": "Hello, this is your GET /vehicles response",
        "vehicles": vehicle_list
    }

    return jsonify(response_body), 200


@app.route('/vehicles/<int:id_vehicle>', methods=['GET'])
def get_vehicle_by_id(id_vehicle):
    vehicles = Vehicle.query.all()
    vehicle_list = list(map(lambda vehicle: vehicle.serialize(), vehicles))

    filtered_vehicles = list(
        filter(lambda vehicle: vehicle['id'] == id_vehicle, vehicle_list))

    if len(filtered_vehicles) == 0:
        return jsonify({"msg": "Vehicle not found"}), 404

    return jsonify(filtered_vehicles[0]), 200

@app.route('/vehicle', methods=['POST'])
def add_vehicle():
    data = request.get_json()
    required_attributes = ['name', 'model', 'vehicle_class', 'manufacturer', 'cost_in_credits', 'length', 'crew', 'passengers', 'max_atmosphering_speed', 'cargo_capacity', 'consumables', 'url', 'description']
    for attribute in required_attributes:
        if attribute not in data:
            return jsonify({"msg": f"Missing {attribute}"}), 400

    existing_vehicle = Vehicle.query.filter_by(name=data['name']).first()
    if existing_vehicle:
        return jsonify({"msg": "Vehicle with that name already exists"}), 400

    new_vehicle = Vehicle(
        name=data['name'],
        model=data['model'],
        vehicle_class=data['vehicle_class'],
        manufacturer=data['manufacturer'],
        cost_in_credits=data['cost_in_credits'],
        length=data['length'],
        crew=data['crew'],
        passengers=data['passengers'],
        max_atmosphering_speed=data['max_atmosphering_speed'],
        cargo_capacity=data['cargo_capacity'],
        consumables=data['consumables'],
        url=data['url'],
        description=data['description']
    )
    db.session.add(new_vehicle)
    db.session.commit()
    return jsonify({"msg": "Vehicle added successfully"}), 201

@app.route('/vehicle/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    
    if not vehicle:
        return jsonify({"msg": "Vehicle not found"}), 404
    
    users = User.query.all()
    for user in users:
        if user.favourites:
            for favourite in user.favourites:
                if favourite.favourite_vehicle == vehicle_id:
                    db.session.delete(favourite)
                    db.session.commit()
    
    db.session.delete(vehicle)
    db.session.commit()    
    return jsonify({"msg": "Vehicle deleted successfully"}), 200

@app.route('/vehicle/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    
    if not vehicle:
        return jsonify({"msg": "Vehicle not found"}), 404
    
    data = request.json
    
    vehicle.name = data.get('name', vehicle.name)
    vehicle.model = data.get('model', vehicle.model)
    vehicle.vehicle_class = data.get('vehicle_class', vehicle.vehicle_class)
    vehicle.manufacturer = data.get('manufacturer', vehicle.manufacturer)
    vehicle.cost_in_credits = data.get('cost_in_credits', vehicle.cost_in_credits)
    vehicle.length = data.get('length', vehicle.length)
    vehicle.crew = data.get('crew', vehicle.crew)
    vehicle.passengers = data.get('passengers', vehicle.passengers)
    vehicle.max_atmosphering_speed = data.get('max_atmosphering_speed', vehicle.max_atmosphering_speed)
    vehicle.cargo_capacity = data.get('cargo_capacity', vehicle.cargo_capacity)
    vehicle.consumables = data.get('consumables', vehicle.consumables)
    vehicle.url = data.get('url', vehicle.url)
    vehicle.description = data.get('description', vehicle.description)
    
    db.session.commit()
    
    return jsonify({"msg": "Vehicle updated successfully"}), 200

@app.route('/starship', methods=['GET'])
def get_starships():
    starships = Starship.query.all()
    if not starships:
        return jsonify({"msg": "No starships found"}), 404

    starship_list = list(map(lambda starship: starship.serialize(), starships))

    response_body = {
        "msg": "Hello, this is your GET /starship response",
        "starships": starship_list
    }

    return jsonify(response_body), 200


@app.route('/starship/<int:id_starship>', methods=['GET'])
def get_starship_by_id(id_starship):
    starships = Starship.query.all()

    starship_list = list(map(lambda starship: starship.serialize(), starships))

    filtered_starships = list(
        filter(lambda starship: starship['id'] == id_starship, starship_list))

    if len(filtered_starships) == 0:
        return jsonify({"msg": "Starship not found"}), 404

    return jsonify(filtered_starships[0]), 200

@app.route('/starship', methods=['POST'])
def add_starship():
    data = request.get_json()
    required_attributes = ['name', 'model', 'starship_class', 'manufacturer', 'cost_in_credits', 'length', 'crew', 'passengers', 'max_atmosphering_speed', 'hyperdrive_rating', 'MGLT', 'cargo_capacity', 'consumables', 'url', 'description']
    for attribute in required_attributes:
        if attribute not in data:
            return jsonify({"msg": f"Missing {attribute}"}), 400

    existing_starship = Starship.query.filter_by(name=data['name']).first()
    if existing_starship:
        return jsonify({"msg": "Starship with that name already exists"}), 400

    new_starship = Starship(
        name=data['name'],
        model=data['model'],
        starship_class=data['starship_class'],
        manufacturer=data['manufacturer'],
        cost_in_credits=data['cost_in_credits'],
        length=data['length'],
        crew=data['crew'],
        passengers=data['passengers'],
        max_atmosphering_speed=data['max_atmosphering_speed'],
        hyperdrive_rating=data['hyperdrive_rating'],
        MGLT=data['MGLT'],
        cargo_capacity=data['cargo_capacity'],
        consumables=data['consumables'],
        url=data['url'],
        description=data['description']
    )
    db.session.add(new_starship)
    db.session.commit()
    return jsonify({"msg": "Starship added successfully"}), 201

@app.route('/starship/<int:starship_id>', methods=['DELETE'])
def delete_starship(starship_id):
    starship = Starship.query.get(starship_id)
    
    if not starship:
        return jsonify({"msg": "Starship not found"}), 404
    
    users = User.query.all()
    for user in users:
        if user.favourites:
            for favourite in user.favourites:
                if favourite.favourite_starship == starship_id:
                    db.session.delete(favourite)
                    db.session.commit()
    
    db.session.delete(starship)
    db.session.commit()    
    return jsonify({"msg": "Starship deleted successfully"}), 200

@app.route('/starship/<int:starship_id>', methods=['PUT'])
def update_starship(starship_id):
    starship = Starship.query.get(starship_id)
    
    if not starship:
        return jsonify({"msg": "Starship not found"}), 404
    
    data = request.json
    
    starship.name = data.get('name', starship.name)
    starship.model = data.get('model', starship.model)
    starship.starship_class = data.get('starship_class', starship.starship_class)
    starship.manufacturer = data.get('manufacturer', starship.manufacturer)
    starship.cost_in_credits = data.get('cost_in_credits', starship.cost_in_credits)
    starship.length = data.get('length', starship.length)
    starship.crew = data.get('crew', starship.crew)
    starship.passengers = data.get('passengers', starship.passengers)
    starship.max_atmosphering_speed = data.get('max_atmosphering_speed', starship.max_atmosphering_speed)
    starship.hyperdrive_rating = data.get('hyperdrive_rating', starship.hyperdrive_rating)
    starship.MGLT = data.get('MGLT', starship.MGLT)
    starship.cargo_capacity = data.get('cargo_capacity', starship.cargo_capacity)
    starship.consumables = data.get('consumables', starship.consumables)
    starship.url = data.get('url', starship.url)
    starship.description = data.get('description', starship.description)
    
    db.session.commit()
    
    return jsonify({"msg": "Starship updated successfully"}), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)