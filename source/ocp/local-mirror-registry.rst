Local Mirror & Registry
=======================

The following Guide will walk through the process of creating a local mirror
and registry for deploying OpenShift on a disconnected network.

Prerequisites
-------------

#. Download the following tools:

   `Openshift Client <https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/openshift-client-linux.tar.gz>`_

   `Mirror Registry for OpenShift <https://developers.redhat.com/content-gateway/rest/mirror/pub/openshift-v4/clients/mirror-registry/latest/mirror-registry.tar.gz>`_

   `Openshift Client Mirror Plugin <https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/oc-mirror.tar.gz>`_

#. SSH to the target server and run the following commands to place the
   binaries in their respective directories.

   .. code-block:: bash

      mkdir ~/mirror-registry
      tar -xzvf mirror-registry.tar.gz -C ~/mirror-registry/
      sudo tar -xzvf openshift-client-linux.tar.gz -C /usr/local/bin/
      sudo tar -xzvf oc-mirror.tar.gz -C /usr/local/bin/
      sudo chmod +x /usr/local/bin/oc-mirror
      sudo rm /usr/local/bin/README.md

Create Local Host Mirror Registry
---------------------------------

Identify Mirror Registry hostname and storage directory variables. In my case
I'm using:

.. code-block:: bash

   quayHostname="mirror.lab.local"
   quayRoot="/mirror/ocp4"
   quayStorage="/mirror/ocp4"
   pgStorage="/mirror/ocp4"
   initPassword="password"

#. Run the following command to install the registry pods as root.

   .. code-block:: bash

      sudo ./mirror-registry install --quayHostname $quayHostname --quayRoot $quayRoot --quayStorage $quayStorage --pgStorage $pgStorage --initPassword $initPassword

   If ran correctly should see a similar ansible recap.

   .. image:: ./images/mirror-reg-install.png

#. Copy newly created root CA, update trust, and open firewall port.

   .. code-block:: bash

      sudo cp /mirror/ocp4/quay-rootCA/rootCA.pem /etc/pki/ca-trust/source/anchors/quayCA.pem
      sudo update-ca-trust extract
      sudo firewall-cmd --add-port=8443/tcp --permanent

#. Test mirror availability via cli.

   .. code-block:: bash

       podman login -u init -p password mirror.lab.local:8443

   .. hint:: Use the "\-\-tls-verify=false" if not adding the rootCA to the trust.

#. Access mirror via browser at `<https://mirror.lab.local:8443>`_

   .. hint:: Username = "init" / Password = "password"

#. If needed the following command will uninstall the registry.

   .. code-block:: bash

      sudo ./mirror-registry uninstall --quayRoot /mirror/ocp4 --quayStorage /mirror/ocp4

Mirror Images to Local Registry
-------------------------------

#. Before mirroring images we need a copy of your Red Hat "Pull Secret" and update
   it with the local mirror information. If you haven't done so download
   `pull secret <https://console.redhat.com/openshift/install/pull-secret>`_

#. Convert "pull secret" to json format.

   .. attention:: You may need to install "jq" for this step.

   .. code-block:: bash

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

   .. code-block:: bash
      :emphasize-lines: 3-5

      {
        "auths": {
          "mirror.lab.local:8443": {
            "auth": "aW5pdDpwYXNzd29yZA=="
          },
          "quay.io": {
            "auth": "b3BlbnNo...",
            "email": "you@example.com"
          },
          "registry.connect.redhat.com": {
            "auth": "NTE3Njg5Nj...",
            "email": "you@example.com"
          },
          "registry.redhat.io": {
            "auth": "NTE3Njg5Nj...",
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

   .. code-block:: bash
      :emphasize-lines: 5,10-12

      kind: ImageSetConfiguration
      apiVersion: mirror.openshift.io/v1alpha2
      storageConfig:
        registry:
          imageURL: mirror.lab.local:8443/mirror/ocp4
          skipTLS: false
      mirror:
        platform:
          channels:
          graph: true
            - name: stable-4.12
              minVersion: 4.12.2
              maxVersion: 4.12.4
        operators:
        - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.12
          packages:
          - name: local-storage-operator
            channels:
              - name: stable
                minVersion: '4.12.0-202302061702'
          - name: odf-operator
            channels:
              - name: stable-4.12
                minVersion: '4.12.0'
          - name: sriov-network-operator
            channels:
              - name: stable
                minVersion: '4.12.0-202302072142'
          - name: lvms-operator
            channels:
              - name: stable-4.12
                minVersion: '4.12.0'
          - name: metallb-operator
            channels:
              - name: stable
                minVersion: '4.12.0-202302141816'
          - name: kubernetes-nmstate-operator
            channels:
              - name: stable
              minVersion: '4.12.0-202302171855'
          - name: kubevirt-hyperconverged
            channels:
              - name: stable
              minVersion: '4.12.1'
          - name: cincinnati-operator
            channels:
              - name: v1
        additionalImages:
        - name: registry.redhat.io/ubi8/ubi:latest
        - name: registry.redhat.io/ubi9/ubi:latest
        - name: quay.io/openshift/origin-sriov-network-device-plugin:4.12
        - name: registry.redhat.io/openshift4/dpdk-base-rhel8  
        - name: docker.io/centos/tools
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

      oc mirror --config=./imageset-config.yaml docker://mirror.lab.local:8443

   .. note:: Be patient this process will take some time to download all the
      requested images.

#. Make note of the following information upon completion. A new directory
   "./oc-mirror-workspace/results-xxxxxxxxxx" with results and yaml files on 
   how to apply mirror to cluster are created.

   .. image:: ./images/mirror-results.png

#. Connect and login to your mirror: `<https://mirror.lab.local:8443>`_
   You should see something similar to the following:

   .. image:: ./images/mirror-images.png

#. Apply the YAML files from the results directory to the cluster.

   .. code-block:: bash

      oc apply -f ./oc-mirror-workspace/results-xxxxxxxxxx/

#. The ability to install operators from the local mirror requires the default
   operator hub to be disabled.

   .. code-block:: bash

      oc patch OperatorHub cluster --type json -p '[{"op": "add", "path": "/spec/disableAllDefaultSources", "value": true}]'

.. attention:: Any update to the operator list requires the "CatalogSource" to
   be updated. 

