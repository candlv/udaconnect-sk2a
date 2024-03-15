** Please be patient while the chart is being deployed **

consumer bootstrap-server: kafka.default.svc.cluster.local:9092
producer bootstrap-server for broker-list:
    kafka-0.kafka-headless.default.svc.cluster.local:9092
    kafka-1.kafka-headless.default.svc.cluster.local:9092
    kafka-2.kafka-headless.default.svc.cluster.local:9092

    PRODUCER:
        kafka-console-producer.sh \            
            --broker-list kafka-0.kafka-headless.default.svc.cluster.local:9092,kafka-1.kafka-headless.default.svc.cluster.local:9092,kafka-2.kafka-headless.default.svc.cluster.local:9092 \
            --topic test

    CONSUMER:
        kafka-console-consumer.sh \            
            --bootstrap-server kafka.default.svc.cluster.local:9092 \
            --topic test \
            --from-beginning

## Test Apache Kafka
### create a pod to use as a Kafka client
kubectl run kafka-client --restart='Never' --image docker.io/bitnami/kafka:3.3.1-debian-11-r25 --namespace default --command -- sleep infinity
kubectl exec --tty -i kafka-client --namespace default -- bash

### create topic
kafka-topics.sh --create --bootstrap-server kafka.default.svc.cluster.local:9092 --replication-factor 1 --partitions 1 --topic test

### Run consumer
kafka-console-consumer.sh --bootstrap-server kafka.default.svc.cluster.local:9092 --topic test --from-beginning

### Run producer
kafka-console-producer.sh --broker-list kafka-0.kafka-headless.default.svc.cluster.local:9092 --topic test
> message 1
> message 2

### export BOOTSTRAP_SERVER
export POD_NAME=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=kafka,app.kubernetes.io/instance=kafka,app.kubernetes.io/component=kafka" -o jsonpath="{.items[0].metadata.name}")
export BOOTSTRAP_SERVER=$(kubectl get pods --namespace default -l "app.kubernetes.io/name=kafka,app.kubernetes.io/instance=udaconnect-kafka,app.kubernetes.io/component=kafka" -o jsonpath="{.items[0].spec.subdomain}")


