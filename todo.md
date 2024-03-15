vagrant up
kubectl apply -f deployment/postgres.yaml
kubectl apply -f deployment/db-configmap.yaml
kubectl apply -f deployment/db-secret.yaml
sh scripts/run_db_command.sh <POD_NAME>

kafka:
  curl https://raw.githubusercontent.com/kubernetes/helm/master/scripts/get-helm-3 > get_helm.sh
  
  chmod 700 get_helm.sh
  
  ./get_helm.sh

  helm repo add bitnami https://charts.bitnami.com/bitnami

  helm install zookeeper bitnami/zookeeper \
  --set replicaCount=3 \
  --set auth.enabled=false \
  --set allowAnonymousLogin=true

  helm install kafka bitnami/kafka \
  --set zookeeper.enabled=false \
  --set replicaCount=3 \
  --set externalZookeeper.servers=zookeeper.default.svc.cluster.local

user-svc: 30001
    remove code
    docker build -t user-svc modules/user-svc
    docker tag user-svc ablazearrow/user-svc:latest
    docker push ablazearrow/user-svc:latest
    
    deploy: 30001
    kubectl apply -f deployment/user-svc.yaml
    postman

location: 30003
    docker build -t location-queue-svc modules/location
    docker tag location-queue-svc ablazearrow/location-queue-svc:latest
    docker push ablazearrow/location-queue-svc:latest
    kubectl apply -f deployment/location-queue-svc.yaml

    kubectl delete deploy produce-svc && kubectl delete service produce-svc
    docker images
    docker rmi -f 

    RUN ["chmod", "+x", "./wrapper_script.sh"]
    CMD ./wrapper_script.sh

produce-location-queue-svc: 30003
    flask simple server
    send to kafka
    docker build -t produce-location-queue modules/location-svc/produce-location-queue-svc
    docker tag produce-location-queue ablazearrow/produce-location-queue:latest
    docker push ablazearrow/produce-location-queue:latest
    deploy: 30003

consume-location-queue-svc: 
    exclude controller and add consumer instead
    connect to kafka
    docker build -t consume-location-queue modules/location-svc/consume-location-queue-svc
    docker tag consume-location-queue ablazearrow/consume-location-queue:latest
    docker push ablazearrow/consume-location-queue:latest
    postman

user-interface-svc: 30000
    ReactRpc
    envoy
    ports in requests
    docker build -t ui-svc modules/ui-svc
    docker tag ui ablazearrow/ui:latest
    docker push ablazearrow/ui:latest
    deploy: 30002
    postman
    modify ui design

connection-svc: 30002
    db.session.query(Person).all()
    python gRPC - utilize existing code
    docker build -t connection-svc modules/connection-svc
    docker tag connection ablazearrow/connection:latest
    docker push ablazearrow/connection:latest

Documents
    Architecture design
    Justify decisions
    OpenAPI
    snap shoots proof work
    rubric review
    submit


kubectl apply -f deployment
kubectl get po



FROM python:3.7-alpine

WORKDIR .

RUN apk add --no-cache gcc musl-dev linux-headers geos libc-dev postgresql-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000

COPY . .
ENTRYPOINT ["/bin/sh"]
CMD ["./wrapper_script.sh"]

RUN ["chmod", "+x", "./wrapper_script.sh"]
CMD ./wrapper_script.sh





#!/bin/bash

# Start the first process
flask run --host 0.0.0.0 &
 
# Start the second process
python ./consumer.py &
  
# Wait for any process to exit
wait -n
  
# Exit with status of process that exited first
exit $?