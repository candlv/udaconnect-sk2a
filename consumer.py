import logging
from json import loads
from app.udaconnect.services import LocationService
from flask_restx import Namespace
from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic

api = Namespace("UdaConnect", description="Connections via geolocation.")  # noqa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("udaconnect-api")

KAFKA_TOPIC = "locations"
KAFKA_DNS = "kafka.default.svc.cluster.local:9092"

consumer = KafkaConsumer(
    KAFKA_TOPIC, bootstrap_servers=[KAFKA_DNS],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='location-g1',
    value_deserializer=lambda x: loads(x.decode('utf-8')))

if KAFKA_TOPIC not in consumer.topics():
    admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_DNS, client_id='locations')
    topic_list = []
    topic_list.append(NewTopic(name="locations", num_partitions=1, replication_factor=1))
    admin_client.create_topics(new_topics=topic_list, validate_only=False)


for location in consumer:
    LocationService.create(location.value)
    logger.info("location_message saved to database")

