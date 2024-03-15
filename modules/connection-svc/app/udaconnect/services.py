import logging
from datetime import datetime, timedelta
from typing import Dict, List
from app import db
from app.udaconnect.models import Connection, Location, Person
from sqlalchemy.sql import text

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-api")

class ConnectionService:
    @staticmethod
    def find_contacts(person_id: int, start_date: datetime, end_date: datetime, meters=5) -> List[Connection]:
        locations: List = db.session.query(Location).filter(Location.person_id == person_id).filter(
            Location.creation_time < end_date).filter(Location.creation_time >= start_date).all()
        # Cache all users in memory for quick lookup
        person_map: Dict[str, Person] = {person.id: person for person in db.session.query(Person).all()}
        # Prepare arguments for queries
        data = []
        for location in locations:
            data.append({
                    "person_id": person_id,
                    "longitude": location.longitude,
                    "latitude": location.latitude,
                    "meters": meters,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": (end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            })
        query = text("""
            SELECT  person_id, id, ST_X(coordinate), ST_Y(coordinate), creation_time
            FROM    location
            WHERE   ST_DWithin(coordinate::geography,ST_SetSRID(ST_MakePoint(:latitude,:longitude),4326)::geography, :meters)
            AND     person_id != :person_id
            AND     TO_DATE(:start_date, 'YYYY-MM-DD') <= creation_time
            AND     TO_DATE(:end_date, 'YYYY-MM-DD') > creation_time;
        """)
        result: List[Connection] = []
        for line in tuple(data):
            for (exposed_person_id, location_id, exposed_lat, exposed_long, exposed_time) in db.engine.execute(query, **line):
                location = Location(id=location_id, person_id=exposed_person_id, creation_time=exposed_time)
                location.set_wkt_with_coords(exposed_lat, exposed_long)
                result.append(Connection(person=person_map[exposed_person_id], location=location))
        return result