import logging, sys
from json import dumps
from app.udaconnect.models import Location
from app.udaconnect.schemas import LocationSchema
from app.udaconnect.services import LocationService
from flask import request
from flask_accepts import accepts, responds
from flask_restx import Namespace, Resource
from kafka import KafkaProducer

logging.basicConfig( level=logging.WARNING)
logger = logging.getLogger("udaconnect-api")
formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s, %(message)s')
stdout = logging.StreamHandler(sys.stdout)
stdout.setFormatter(formatter)
logger.addHandler(stdout)

DATE_FORMAT = "%Y-%m-%d"
api = Namespace("UdaConnect", description="Connections via geolocation.")  # noqa

KAFKA_TOPIC = "locations"
BROKER = "kafka-0.kafka-headless.default.svc.cluster.local:9092"

producer = KafkaProducer(bootstrap_servers=[BROKER])

@api.route("/locations")
@api.route("/locations/<location_id>")
@api.param("location_id", "Unique ID for a given Location", _in="query")
class LocationResource(Resource):
    @responds(schema=LocationSchema)
    def get(self, location_id) -> Location:
        location: Location = LocationService.retrieve(location_id)
        return location

    @accepts(schema=LocationSchema)
    def post(self) -> Location:
        location = request.get_json()
        producer.send(KAFKA_TOPIC, dumps(location).encode('utf-8'))
        producer.flush()
        logger.warning('{} Saved into kafka'.format(location)) 
        
        return ({"status": "ok", "message": "{} Saved into kafka".format(location)})