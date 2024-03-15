import os
from app import create_app
import logging, sys
from json import loads
from app.udaconnect.services import LocationService
from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic

logging.basicConfig( level=logging.WARNING)
logger = logging.getLogger("udaconnect-api")
formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s, %(message)s')
stdout = logging.StreamHandler(sys.stdout)
stdout.setFormatter(formatter)
logger.addHandler(stdout)

KAFKA_TOPIC = "locations"
KAFKA_DNS = "kafka.default.svc.cluster.local:9092"

consumer = KafkaConsumer(
    KAFKA_TOPIC, bootstrap_servers=[KAFKA_DNS],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='location-g1')

if KAFKA_TOPIC not in consumer.topics():
    admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_DNS, client_id='locations')
    topic_list = []
    topic_list.append(NewTopic(name="locations", num_partitions=1, replication_factor=1))
    admin_client.create_topics(new_topics=topic_list, validate_only=False)


app = create_app(os.getenv("FLASK_ENV") or "test")

if __name__ == "__main__":
    app.run(debug=True)
    while True:
        for location in consumer:
            msg = location.value 
            location_msg = loads(msg.decode('utf-8'))
            response = LocationService.create(location_msg)  
            logger.warning('{} Saved to Database'.format(response))       
