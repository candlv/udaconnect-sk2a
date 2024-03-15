import logging, sys
from typing import Dict

from app import db
from app.udaconnect.models import Location
from app.udaconnect.schemas import LocationSchema
from geoalchemy2.functions import ST_Point

logging.basicConfig( level=logging.WARNING)
logger = logging.getLogger("udaconnect-api")
formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s, %(message)s')
stdout = logging.StreamHandler(sys.stdout)
stdout.setFormatter(formatter)
logger.addHandler(stdout)

class LocationService:
    @staticmethod
    def retrieve(location_id) -> Location:
        location, coord_text = (
            db.session.query(Location, Location.coordinate.ST_AsText())
            .filter(Location.id == location_id).one()
        )
        location.wkt_shape = coord_text
        return location

    @staticmethod
    def create(location: Dict) -> Location:
        validation_results: Dict = LocationSchema().validate(location)
        if validation_results:
            logger.warning('Unexpected data format in {}'.format(validation_results))
            raise Exception('Invalid {}'.format(validation_results))

        new_location = Location()
        new_location.person_id = location["person_id"]
        new_location.creation_time = location["creation_time"]
        new_location.coordinate = ST_Point(location["latitude"], location["longitude"])
        db.session.add(new_location)
        db.session.commit()        
        return new_location