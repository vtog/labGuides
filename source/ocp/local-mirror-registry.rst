Local Mirror & Registry
=======================

The following Guide will walk through the process of creating a local mirror
and registry for deploying OpenShift on a disconnected network.

Prerequisites
-------------

#. Download the following files and copy to the destination server.

   `Openshift Client <https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/openshift-client-linux.tar.gz>`_

   `Mirror Registry for OpenShift <https://developers.redhat.com/content-gateway/rest/mirror/pub/openshift-v4/clients/mirror-registry/latest/mirror-registry.tar.gz>`_

   `Openshift Client Mirror Plugin <https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/oc-mirror.tar.gz>`_

   `Your Pull Secret <https://console.redhat.com/openshift/install/pull-secret>`_

   .. attention:: These links point to the most recent versions. Typically
      you'll want a specific version. You can find those here:
 
      `<https://access.redhat.com/downloads/content/290/>`_

#. SSH to the target server and run the following commands to place the
   binaries in their respective directories.

   .. code-block:: bash

      mkdir ~/mirror-registry
      tar -xzvf mirror-registry-1.3.6.tar.gz -C ~/mirror-registry/
      tar -xzvf oc-4.13.1-linux.tar.gz -C ~/.local/bin
      tar -xzvf oc-mirror.tar.gz -C ~/.local/bin
      chmod +x ~/.local/bin/oc-mirror
      rm ~/.local/bin/README.md

#. Create the target directory for the new registry. In my lab we're using
   "/mirror"

   .. code-block:: bash

      sudo mkdir /mirror

#. Identify and create the **Hostname** and **Directory** session variables. In
   my case I'm using the following for my lab:

   .. important:: For "quayHostname" be sure to use a name that can be resolved
      via DNS or the local hosts file. The installer will use that name to
      validate the service.

   .. note:: The "ocp4" directory in "/mirror" will be created by the installer.

   .. code-block:: bash

      quayHostname="mirror.lab.local"
      quayRoot="/mirror/ocp4"
      quayStorage="/mirror/ocp4"
      pgStorage="/mirror/ocp4"
      initPassword="password"

Create Local Host Mirror Registry
---------------------------------

#. Run the following command to install the registry pods as root.

   .. important:: The registry services will be run as root. You can see the
      pods with ``sudo podman ps``

   .. warning:: Installing as "root" will force IPv4 only listener.

   .. code-block:: bash

      cd ~/mirror-registry

      sudo ./mirror-registry install --quayHostname $quayHostname --quayRoot $quayRoot --quayStorage $quayStorage --pgStorage $pgStorage --initPassword $initPassword

   If ran correctly should see a similar ansible recap.

   .. image:: ./images/mirror-reg-install.png

#. Copy newly created root CA, update trust, and open firewall port.

   .. code-block:: bash

      sudo cp $quayRoot/quay-rootCA/rootCA.pem /etc/pki/ca-trust/source/anchors/quayCA.pem
      sudo update-ca-trust extract
      sudo firewall-cmd --add-port=8443/tcp --permanent

#. Test mirror availability via cli. The following command should return
   "Login Succeeded!" if everything is working.

   .. code-block:: bash

       podman login -u init -p password $quayHostname:8443

   .. hint:: Use the "\-\-tls-verify=false" if not adding the rootCA to the trust.

#. Access mirror via browser at `<https://$quayHostname:8443>`_

   .. hint:: Username = "init" / Password = "password"

#. If something went wrong, the following command will **UNINSTALL** the
   registry.

   .. code-block:: bash

      sudo ./mirror-registry uninstall --quayRoot $quayRoot --quayStorage $quayStorage

Mirror Images to Local Registry
-------------------------------

#. Before mirroring images we need a copy of your Red Hat "Pull Secret" and update
   it with the local mirror information. If you haven't done so download it here:
   `your pull secret <https://console.redhat.com/openshift/install/pull-secret>`_

#. Convert "pull secret" to json format.

   .. attention:: You may need to install "jq" for this step.

   .. code-block:: bash

      cd ~
      cat ./pull-secret.txt | jq . > ./pull-secret.json

#. Copy pull-secret.json to ~/.docker and rename config.json

   .. code-block:: bash

      mkdir ~/.docker
      cp ./pull-secret.json ~/.docker/config.json

#. Generate the base64-encoded user name and password for mirror registry.

   .. code-block:: bash

      echo -n 'init:password' | base64 -w0

#. Modify ~/.docker/config.json by adding local mirror information. Use the
   previous steps encoded output for "auth".

   .. code-block:: json
      :emphasize-lines: 3-5

      {
        "auths": {
          "$quayHostname:8443": {
            "auth": "aW5pdDpwYXNzd29yZA=="
          },
          "cloud.openshift.com": {
            "auth": "b3BlbnNo...",
            "email": "you@example.com"
          },
          "quay.io": {
            "auth": "b3BlbnNo...",
            "email": "you@example.com"
          },
          "registry.connect.redhat.com": {
            "auth": "fHVoYy1w...",
            "email": "you@example.com"
          },
          "registry.redhat.io": {
            "auth": "fHVoYy1w...",
            "email": "you@example.com"
          },
          "registry6.redhat.io": {
            "auth": "fHVoYy1w...",
            "email": "you@example.com"
          }
        }
      }

#. Create the following "imageset-config.yaml" file. In the file below I'm
   mirroring OCP v4.12, more specifically only v4.12.2. I've also added some
   additional operators and images.

   .. important:: Be sure path in imageURL (line 5) matches the path assigned
      earlier for "quayRoot".
   
   .. note:: "graph: true" mirror's the graph data to our disconnected registry
      which enables our disconnected clusters to show the visual of what
      versions we can update to.

   .. note:: "shortestPath: true" instructs the mirror to only pull the
      required version to upgrade from one version to the next.

   .. attention:: The example here shows an ImageSet that includes both 4.12.x
      and 4.13.x images and operators.

   .. code-block:: yaml
      :emphasize-lines: 5,10-13,15,25

      kind: ImageSetConfiguration
      apiVersion: mirror.openshift.io/v1alpha2
      storageConfig:
        registry:
          imageURL: $quayHostname:8443$quayStorage
          skipTLS: false
      mirror:
        platform:
          channels:
            - name: stable-4.13
              minVersion: 4.12.18
              shortestPath: true
          graph: true
        operators:
          - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.12
            packages:
              - name: cincinnati-operator
              - name: kubernetes-nmstate-operator
              - name: kubevirt-hyperconverged
              - name: local-storage-operator
              - name: lvms-operator
              - name: metallb-operator
              - name: odf-operator
              - name: skupper-operator
              - name: sriov-network-operator
          - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.13
            packages:
              - name: cincinnati-operator
              - name: kubernetes-nmstate-operator
              - name: kubevirt-hyperconverged
              - name: local-storage-operator
              - name: lvms-operator
              - name: metallb-operator
              - name: odf-operator
              - name: skupper-operator
              - name: sriov-network-operator
        additionalImages:
          - name: registry.redhat.io/ubi8/ubi:latest
          - name: registry.redhat.io/ubi9/ubi:latest
          - name: registry.redhat.io/ubi9/httpd-24:latest
          - name: registry.redhat.io/ubi9/nginx-122:latest
          - name: registry.redhat.io/rhel8/support-tools:latest
          - name: registry.redhat.io/rhel9/support-tools:latest
          - name: registry.redhat.io/openshift4/performance-addon-operator-must-gather-rhel8:v4.12
          - name: registry.redhat.io/openshift4/performance-addon-operator-must-gather-rhel8:v4.13
          - name: registry.redhat.io/openshift4/dpdk-base-rhel8:latest
          - name: quay.io/openshift/origin-sriov-network-device-plugin:latest
          - name: docker.io/centos/tools:latest
          - name: docker.io/f5devcentral/f5-hello-world:latest
          - name: docker.io/library/httpd:latest
          - name: docker.io/library/nginx:latest
        helm: {}

   .. tip:: To discover operators by their package name, applicable channels,
      and versions use the following commands.

      .. code-block:: bash

         # List ALL available operators
         oc mirror list operators --catalog registry.redhat.io/redhat/redhat-operator-index:v4.12

         # List package specific inormation for an operator
         oc mirror list operators --package sriov-network-operator --catalog registry.redhat.io/redhat/redhat-operator-index:v4.12

#. Mirror the registry.

   .. attention:: oc-mirror requires OpenShift v4.9.x and later.

   .. code-block:: bash

      oc mirror --config=./imageset-config.yaml docker://$quayHostname:8443

   .. note:: Be patient this process will take some time to download all the
      requested images.

#. Make note of the following information upon completion. A new directory
   "./oc-mirror-workspace/results-xxxxxxxxxx" with results and yaml files on 
   how to apply mirror to cluster are created.

   .. image:: ./images/mirror-results.png

#. Connect and login to your mirror: `<https://$quayHostname:8443>`_
   You should see something similar to the following:

   .. image:: ./images/mirror-images.png

Update Running Cluster
----------------------

A running cluster needs to be updated to use the new registry/mirror.
To create a new cluster using the local mirror & registry see:
`Agent-Based Install Notes <./agent-based-installer-notes.html>`_

#. Extract OCP pull-secret. A new local file ``.dockerconfigjson`` is created.
 
   .. code-block:: bash
 
      oc extract secret/pull-secret -n openshift-config --confirm --to=.
      cat ./.dockerconfigjson | jq . > ./.dockerconfig.json
 
#. Update ``.dockerconfig.json`` with local registry credentials.
 
   .. code-block:: json
 
      {
        "auths": {
          "mirror.lab.local:8443": {
            "auth": "aW5pdDpwYXNzd29yZA=="
          }
        }
      }
 
      
#. Import the new pull-secret.

   .. code-block:: bash

      oc set data secret/pull-secret -n openshift-config --from-file=.dockerconfigjson=.dockerconfig.json

#. Create configmap of quay-rootCA.

   .. code-block:: bash

      oc create configmap registry-config --from-file=$quayHostname..8443=/mirror/ocp4/quay-rootCA/rootCA.pem

#. Add quay-rootCA to cluster.

   .. code-block:: bash

      oc patch image.config.openshift.io/cluster --patch '{"spec":{"additionalTrustedCA":{"name":"registry-config"}}}' 

#. Apply the YAML files from the results directory to the cluster.

   .. note:: Everytime you successfully run "oc mirror" a "results" dir is
      created.

   .. code-block:: bash

      oc apply -f ./oc-mirror-workspace/results-xxxxxxxxxx/

#. The ability to install operators from the local mirror requires the default
   operator hub to be disabled.

   .. code-block:: bash

      oc patch OperatorHub cluster --type json -p '[{"op": "add", "path": "/spec/disableAllDefaultSources", "value": true}]'

   .. attention:: Any change to the operator list requires the "CatalogSource"
      to be updated. To do so run "oc remove" and "oc create" of the
      "CatalogSource".

