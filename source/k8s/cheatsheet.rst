Cheat-Sheet
===========

- Find object shortnames by querying api

  .. code-block:: bash

     kubectl api-resources | less

- Get all resources

  .. code-block:: bash

     kubectl get all -A

- View the YAML declaration specification

  .. code-block:: bash

     kubectl explain pod.spec.restartPolicy

Pods
----

- Run new pod in default namespace

  .. code-block:: bash
   
     kubectl run nginx --image=nginx

- Get pods

  .. code-block:: bash

     kubectl get pods -o wide

- Get pods yaml

  .. code-block:: bash

     kubectl get pods -o yaml
  
- Get pod or container logs

  .. code-block:: bash
  
     kubectl logs pod/nginx

  .. code-block:: bash

     kubectl logs pod/nginx -c sidecar

- Describe pod

  .. code-block:: bash

     kubectl describe pod/nginx

- Get events

  .. code-block:: bash

     kubectl events

- Get pod IP

  .. code-block:: bash
  
     NGINX_IP=$(kubectl get pods -o wide | awk '/nginx/ { print $6 }'); echo $NGINX_IP
  
- Expose pod on port 80 (Use ctrl-c to close)

  .. code-block:: bash
  
     kubectl port-forward pod/nginx 8080:80
  
- Run curl pod

  .. code-block:: bash
  
     kubectl run -it --rm curl --image=curlimages/curl:latest --restart=Never -- http://$NGINX_IP
  
- Run pod and pass env variable to container

  .. code-block:: bash
  
     kubectl run --image=nginx nginx --env="NGINX_IP=$NGINX_IP" -- sleep infinity
  
- Excecut shell process

  .. code-block:: bash

     kubectl exec -it nginx -- bash
  
- Create yaml from dry-run

  .. code-block:: bash
  
     kubectl run nginx --image=nginx --dry-run=client -o yaml | tee nginx.yaml
  
- Create or Apply yaml

  .. code-block:: bash
  
     kubectl create -f nginx.yaml
  
     kubectl apply -f nginx.yaml

- Replace running pod

  .. code-block:: bash

     kubectl replace --force=true --grace-period=0 -f nginx.yaml

- Get previous logs after restart

  .. code-block:: bash

     kubectl logs -p nginx

- Delete pod
 
  .. code-block:: bash
  
     kubectl delete pod/nginx --now
  
Namespaces
----------

- Get namespace

  .. code-block:: bash

     kubectl get ns

- Create a new namespace

  .. code-block:: bash

     kubectl create ns mynamespace

- Get config view

  .. code-block:: bash

     kubectl config view

- Set config namespace

  .. code-block:: bash

     kubectl config set-context --current -n mynamespace

Deployment and ReplicaSets
--------------------------

- Create a simple deployment and apply it

  .. code-block:: bash

     kubectl create deployment nginx --image=nginx --dry-run=client -o yaml | tee nginx-deployment.yaml | kubectl apply -f -

- Get deployments

  .. code-block:: bash

     kubectl get deployment -o wide

- Get deployment yaml

  .. code-block:: bash

     kubectl get deployment/nginx -o yaml

- Describe the deployment
 
  .. code-block:: bash
 
     kubectl describe deployment/nginx

- Get replicasets

  .. code-block:: bash

     kubectl get replicaset -o wide

- Get deployment rollout history

  .. code-block:: bash

     kubectl rollout history deployment/nginx

- Annotate deployment

  .. code-block:: bash

     kubectl annotate deployment/nginx kubernetes.io/change-cause="initial deployment"

- Scale deployment

  .. code-block:: bash

     kubectl scale deployment/nginx --replicas=10

- Check rollout status

  .. code-block:: bash

     kubectl rollout status deployment/nginx

- Change deployment image and watch rollout via cli

  .. code-block:: bash

     kubectl set image deployment/nginx nginx=nginx:alpine && kubectl rollout status deployment/nginx

- Undo last rollout

  .. code-block:: bash

     kubectl rollout undo deployment/nginx && kubectl rollout status deployment/nginx

- Undo rollout to specific revision

  .. code-block:: bash

     kubectl rollout undo deployment/nginx --to-revision=1 && kubectl rollout status deployment/nginx

DaemonSets
----------

Example of creating a Daemonset from a Deployment yaml

- Create deployment

  .. code-block:: bash

     kubectl create deployment nginx --image=nginx --dry-run=client -o yaml | tee nginx-deployment.yaml

- Modify the deployment by removing "replicas" and "strategy" from the yaml and
  add the following highlighted changes.

  .. code-block:: bash
     :emphasize-lines: 3,20-24

     cat <<EOF > nginx-daemonset.yaml
     apiVersion: apps/v1
     kind: DaemonSet
     metadata:
       labels:
         app: nginx
       name: nginx
     spec:
       selector:
         matchLabels:
           app: nginx
       template:
         metadata:
           labels:
             app: nginx
         spec:
           containers:
           - image: nginx
             name: nginx
             env:
             - name: NODE_NAME
               valueFrom:
                 fieldRef:
                   fieldPath: spec.nodeName
     EOF

- Apply/create new DaemonSet

  .. code-block:: bash

     kubectl apply -f nginx-daemonset.yaml

- Get DaemonSet

  .. code-block:: bash

     kubectl get daemonset

Set Image & Kubectl Patch
-------------------------

.. tip:: To convert yaml to json install ``yq`` 

   .. code-block:: bash

      wget -qO /usr/local/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_$(dpkg --print-architecture) && chmod +x /usr/local/bin/yq

- Show help

  .. code-block:: bash

     kubectl set image --help | less

- Create a pod

  .. code-block:: bash

     kubectl run nginx --image=nginx

- Set pod image

  .. code-block:: bash

     kubectl set image pod/nginx nginx=nginx:alpine-slim

- Use wildcard when multiple containers running

  .. code-block:: bash

     kubectl set image pod/nginx *=nginx:stable

- Create a deployment

  .. code-block:: bash

     kubectl create deployment web --image=nginx --replicas=3

- Set deployment image and watch rollout

  .. code-block:: bash

     kubectl set image deployment/web nginx=nginx:alpine-slim; kubectl rollout status deployment/web

- Create example patch yaml

  .. code-block:: bash

     cat <<EOF > patch.yaml
     spec:
       template:
         spec:
           containers:
           - image: nginx
             name: nginx
     EOF

- Another example patch yaml

  .. code-block:: bash

     cat <<EOF > patch.yaml
     spec:
       template:
         spec:
           containers:
           - image: ubuntu
             name: ubuntu
             args:
             - sleep
             - infinity
     EOF

- Apply patch
 
  .. code-block:: bash  
 
     kubectl patch deployment web --patch-file=patch.yaml

- Convert yaml to one-line of json

  .. code-block:: bash

     cat patch.yaml | yq -o=json -I=0

- Use json to apply patch (from previous yaml examples

  .. code-block:: bash

     kubectl patch deployment web -p '{"spec":{"template":{"spec":{"containers":[{"image":"nginx","name":"nginx"}]}}}}'

     kubectl patch deployment web -p '{"spec":{"template":{"spec":{"containers":[{"image":"ubuntu","name":"ubuntu","args":["sleep","infinity"]}]}}}}'

- Add or Remove container with patch

  .. code-block:: bash

     kubectl patch deployment web --type=json -p '[{"op":"add","path":"/spec/template/spec/containers/-","value":{"name":"busybox","image":"busybox","args":["sleep","infinity"]}}]'

     kubectl patch deployment web --type=json -p '[{"op":"remove","path":"/spec/template/spec/containers/2"}]'

Services
--------

Explore ClusterIP, NodePort, LoadBalancer

ClusterIP
~~~~~~~~~

- Create deployment

  .. code-block:: bash

     kubectl create deployment nginx --image=spurin/nginx-debug --port=80 --replicas=3 -o yaml --dry-run=client

     kubectl create deployment nginx --image=spurin/nginx-debug --port=80 --replicas=3

- Expose deployment

  .. code-block:: bash

     kubectl expose deployment/nginx --dry-run=client -o yaml

     kubectl expose deployment/nginx

- Get service

  .. code-block:: bash

     kubectl get service

- Get endpoints

  .. code-block:: bash

     kubectl get endpoints

- Get pods (Correlate pod IP with EndPoint)

  .. code-block:: bash

     kubectl get pods -o wide

- Describe service

  .. code-block:: bash

     kubectl describe service/nginx

- Capture ClusterIP and curl IP

  .. code-block:: bash

     CLUSTER_IP=$(kubectl get services | grep ClusterIP | grep nginx | awk {'print $3'}); echo $CLUSTER_IP

     curl $CLUSTER_IP

- Use curl container to curl website

  .. code-block:: bash

     kubectl run --rm -it curl --image=curlimages/curl:8.4.0 --restart=Never -- sh

     curl nginx.default.svc.cluster.local

     exit

- Delete service

  .. code-block:: bash

     kubectl delete service/nginx

NodePort
~~~~~~~~

- Create deployment

  .. code-block:: bash

     kubectl create deployment nginx --image=spurin/nginx-debug --port=80 --replicas=3

- Expose service

  .. code-block:: bash

     kubectl expose deployment/nginx --type=NodePort

- Get service

  .. code-block:: bash

     kubectl get service

- Describe service

  .. code-block:: bash

     kubectl describe service/nginx

- Get nodes

  .. code-block:: bash

     kubectl get nodes -o wide

- Find IP:PORT and curl service

  .. code-block:: bash

     CONTROL_PLANE_IP=$(kubectl get nodes -o wide | grep control-plane | awk {'print $6'}); echo $CONTROL_PLANE_IP

     NODEPORT_PORT=$(kubectl get services | grep NodePort | grep nginx | awk -F'[:/]' '{print $2}'); echo $NODEPORT_PORT

     curl ${CONTROL_PLANE_IP}:${NODEPORT_PORT}

- Delete service

  .. code-block:: bash

     kubectl delete service/nginx

LoadBalancer
~~~~~~~~~~~~

- Create deployment

  .. code-block:: bash

     kubectl create deployment nginx --image=spurin/nginx-debug --port=80 --replicas=3

- Expose service

  .. code-block:: bash

     kubectl expose deployment/nginx --type=LoadBalancer --port 8080 --target-port 80

- Describe service

  .. code-block:: bash

     kubectl describe svc/nginx

- Capture IP and Port curl and watch endpoints

  .. code-block:: bash

     LOADBALANCER_IP=$(kubectl get service | grep LoadBalancer | grep nginx | awk '{split($0,a," "); split(a[4],b,","); print b[1]}'); echo $LOADBALANCER_IP

     LOADBALANCER_PORT=$(kubectl get service | grep LoadBalancer | grep nginx | awk -F'[:/]' '{print $2}'); echo $LOADBALANCER_PORT

     watch --differences "curl ${LOADBALANCER_IP}:${LOADBALANCER_PORT} 2>/dev/null"

     ctrl-c

- Delete service and deployment

  .. code-block:: bash

     kubectl delete deployment/nginx service/nginx

ExternalName
~~~~~~~~~~~~

- Create two deployments

  .. code-block:: bash

     kubectl create deployment nginx-red --image=spurin/nginx-red --port=80

     kubectl create deployment nginx-blue --image=spurin/nginx-blue --port=80

- Get deployments

  .. code-block:: bash

     kubectl get deployment

- Expose two services

  .. code-block:: bash

     kubectl expose deployment/nginx-red

     kubectl expose deployment/nginx-blue

- Get service

  .. code-block:: bash

     kubectl get service

- Create service

  .. code-block:: bash

     kubectl create service externalname my-service --external-name nginx-red.default.svc.cluster.local

- Get service

  .. code-block:: bash
   
     kubectl get service

- Test service

  .. code-block:: bash

     kubectl run --rm -it curl --image=curlimages/curl:8.4.0 --restart=Never -- sh

     curl nginx-red

     curl nginx-blue

     curl my-service

     nslookup my-service

     exit

- Delete deployment and servcies

  .. code-block:: bash

     kubectl delete deployment/nginx-blue deployment/nginx-red service/nginx-blue service/nginx-red service/my-service

Headless
~~~~~~~~

- Create deployment

  .. code-block:: bash

     kubectl create deployment nginx --image=spurin/nginx-debug --replicas=3 --port=80

- Create expose yaml

  .. code-block:: bash

     kubectl expose deployment/nginx --dry-run=client -o yaml --type=ClusterIP | tee headless.yaml

- Set "ClusterIP: None", cat results

  .. code-block:: bash

     grep -q 'clusterIP: None' headless.yaml || sed -i '/spec:/a\ \ clusterIP: None' headless.yaml; cat headless.yaml

- Apply yaml

  .. code-block:: bash

     kubectl apply -f headless.yaml

- Get service

  .. code-block:: bash

     kubectl get service

- Curl service

  .. code-block:: bash

     kubectl run --rm -it curl --image=curlimages/curl:8.4.0 --restart=Never -- sh

     watch nslookup nginx

     curl nginx

     exit

- Delete deployment and servce

  .. code-block:: bash

     kubectl delete deployment/nginx service/nginx

Jobs & CronJobs
---------------

Jobs
~~~~

- Create job to calculate pi

  .. code-block:: bash

     kubectl create job calculatepi --image=perl:5.34.0 -- "perl" "-Mbignum=bpi" "-wle" "print bpi(2000)"

- Watch jobs

  .. code-block:: bash

     watch kubectl get jobs

- Describe job

  .. code-block:: bash

     kubectl describe job/calculatepi

- Get running pods

  .. code-block:: bash

     kubectl get pods -o wide

- Capture pod name

  .. code-block:: bash

     PI_POD=$(kubectl get pods | grep calculatepi | awk {'print $1'}); echo $PI_POD

- Show pod logs

  .. code-block:: bash

     kubectl logs $PI_POD

- Delete job

  .. code-block:: bash

     kubectl delete job/calculatepi

- Create job yaml

  .. code-block:: bash

     kubectl create job calculatepi --image=perl:5.34.0 --dry-run=client -o yaml -- "perl" "-Mbignum=bpi" "-wle" "print bpi(2000)" | tee calculatepi.yaml

- Use explain to review options

  .. code-block:: bash

     kubectl explain job.spec | less

- Add "completions" and "parallelism"

   .. code-block:: bash
      :emphasize-lines: 8,9

      cat <<EOF > calculatepi.yaml
      apiVersion: batch/v1
      kind: Job
      metadata:
        creationTimestamp: null
        name: calculatepi
      spec:
        completions: 20
        parallelism: 5
        template:
          metadata:
            creationTimestamp: null
          spec:
            containers:
            - command:
              - perl
              - -Mbignum=bpi
              - -wle
              - print bpi(2000)
              image: perl:5.34.0
              name: calculatepi
              resources: {}
            restartPolicy: Never
      status: {}
      EOF

- Apply job yaml and watch pods

  .. code-block:: bash

     kubectl apply -f calculatepi.yaml && sleep 1 && watch kubectl get pods -o wide

- Show logs from one of the pods

  .. code-block:: bash

     PI_POD=$(kubectl get pods | grep calculatepi | tail -1 | awk {'print $1'}); kubectl logs $PI_POD

- Delete job

  .. code-block:: bash

     kubectl delete job/calculatepi

CronJobs
~~~~~~~~

- Create cronjob

  .. code-block:: bash

     kubectl create cronjob calculatepi --image=perl:5.34.0 --schedule="* * * * *" -- "perl" "-Mbignum=bpi" "-wle" "print bpi(2000)"

- Watch jobs

  .. code-block:: bash

     watch kubectl get jobs

- Edit cronjob; Add ``completions: 20`` and ``parallelism: 5`` to
  ``spec.JobTemplate.spec``

  .. code-block:: bash

     kubectl edit cronjob/calculatepi

     :wq!

- Watch jobs

  .. code-block:: bash

     watch kubectl get jobs

- Delete 

  .. code-block:: bash

     kubectl delete cronjob/calculatepi

ConfigMaps
----------

- Create configmap ``--from-literal``

  .. code-block:: bash

     kubectl create configmap color-configmap --from-literal=COLOUR=red --from-literal=KEY=value

- Create configmap ``--from-env-file``

  .. code-block:: bash
    
     cat <<EOF > configmap-color.properties
     COLOUR=green
     KEY=value
     EOF

  .. code-block:: bash

     kubectl create configmap color-configmap --from-env-file=configmap-color.properties

- Describe configmap

  .. code-block:: bash

     kubectl describe configmap/color-configmap

- Create pod yaml and reference configmap

  .. code-block:: bash
     :emphasize-lines: 18-20

     cat <<EOF > env-dump-pod.yaml
     apiVersion: v1
     kind: Pod
     metadata:
       creationTimestamp: null
       labels:
         run: ubuntu
       name: ubuntu
     spec:
       containers:
       - command:
         - bash
         - -c
         - env; sleep infinity
         image: ubuntu
         name: ubuntu
         resources: {}
         envFrom:
         - configMapRef:
             name: color-configmap
       dnsPolicy: ClusterFirst
       restartPolicy: Never
     status: {}
     EOF

- Apply pod yaml

  .. code-block:: bash

     kubectl apply -f env-dump-pod.yaml

- Check pod logs to verify key-pairs are applied

  .. code-block:: bash

     kubectl logs ubuntu

- After updating configmap the previously crated pod will need to be deleted
  and recreated to see change

  .. code-block:: bash

     kubectl delete -f env-dump-pod.yaml --now; kubectl apply -f env-dump-pod.yaml

- Delete configmap

  .. code-block:: bash

     kubectl delete configmap/color-configmap

Secrets
-------

.. tip:: Base64 encode and decode

   .. code-block:: bash

      echo -n value | base64

   .. code-block:: bash

      echo dmFsdWU= | base64 -d

- Create secret ``--from-literal``

  .. code-block:: bash

     kubectl create secret generic color-secret --from-literal=COLOUR=red --from-literal=KEY=value

- Get secrets

  .. code-block:: bash

     kubectl get secrets

- Show secret yaml

  .. code-block:: bash

     kubectl get secret/color-secret -o yaml

- Create ubunto pod

  .. code-block:: bash

     cat <<EOF > env-dump-pod.yaml
     apiVersion: v1
     kind: Pod
     metadata:
       creationTimestamp: null
       labels:
         run: ubuntu
       name: ubuntu
     spec:
       containers:
       - command:
         - bash
         - -c
         - env; sleep infinity
         image: ubuntu
         name: ubuntu
         resources: {}
         envFrom:
         - secretRef:
             name: color-secret
       dnsPolicy: ClusterFirst
       restartPolicy: Never
     status: {}
     EOF

- Create pod

  .. code-block:: bash

     kubectl apply -f env-dump-pod.yaml

- Check pod logs to verify key-pairs are applied
 
  .. code-block:: bash

     kubectl logs ubuntu

- Delete pod

  .. code-block:: bash

     kubectl delete pod/ubuntu secret/color-secret --now

Labels
------

- Run pod and expose service

  .. code-block:: bash

     kubectl run nginx --image nginx --port 80

     kubectl expose pod/nginx

- Query objects with ``--selector``

  .. code-block:: bash

     kubectl get all --selector run=nginx

- Add label to pod

  .. code-block:: bash

     kubectl label pod/nginx vince=test

- Query objects with ``--selector``      
                                         
  .. code-block:: bash                   
                                         
     kubectl get all --selector vince=test

Annotations
-----------

- Create a deployment with annotations

  .. code-block:: bash
     :emphasize-lines: 7-9,20-21

     cat <<EOF > annotations.yaml
     apiVersion: apps/v1
     kind: Deployment
     metadata:
       labels:
         app: web
       annotations:
         company.org/owner: "team-vtog"
         company.org/ticket: "5150"
       name: web
     spec:
       replicas: 1
       selector:
         matchLabels:
           app: web
       template:
         metadata:
           labels:
             app: web
           annotations:
             company.org/note: "This will land on a pod"
         spec:
           containers:
           - image: nginx
             name: nginx
     EOF

- Apply deployment

  .. code-block:: bash

     kubectl apply -f annotations.yaml

- Describe deployment and check annotations

  .. code-block:: bash

     kubectl describe deployment/web | less

- Describe pod and check annotations

  .. code-block:: bash

     kubectl describe pod -l app=web | less
