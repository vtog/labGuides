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

- quayHostname = "mirror.lab.local"
- quayRoot     = "/mirror/ocp4"
- quayStorage  = "/mirror/ocp4"
- pgStorage    = "/mirror/ocp4"
- initPassword = "password"

#. Run the following command to install the registry pods as root.

   .. code-block:: bash

      sudo ./mirror-registry install --quayHostname mirror.lab.local --quayRoot /mirror/ocp4 --quayStorage /mirror/ocp4 --pgStorage /mirror/ocp4 --initPassword password

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

   .. hint:: Use the "--tls-verify=false" if not adding the rootCA to the trust.

#. Access mirror via browser at `<https://mirror.lab.local:8443>`_

   .. hint:: Username = "init" / Password = "password"

Mirror Images to Local Registry
-------------------------------

#. Before mirroring images we need a copy of your Red Hat "Pull Secret" and update
   it with the local mirror information. If you haven't done so download
   `pull secret <https://console.redhat.com/openshift/install/pull-secret>`_

#. Convert "pull secret" to json format.

   .. code-block:: bash

      cat ./pull-secret.txt | jq . > ./pull-secret.json

   .. attention:: You may need to install "jq" for this step.

#. Copy pull-secret.json to ~/.docker and rename config.json

   .. code-block:: bash

      cp ./pull-secret.json ~/.docker/config.json

   .. attention:: You man need to create ~/.docker directory.

#. Generate the base64-encoded user name and password for mirror registry.

   .. code-block:: bash

      echo -n 'init:password' | base64 -w0

#. Modify ~/.docker/config.json by adding local mirror information. Use the
   previous steps encode output for "auth".

   .. code-block:: bash
      :emphasize-lines: 3-5

      {
        "auths": {
          "mirror.lab.local:8443": {
            "auth": "aW5pdDpwYXNzd29yZA==",
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
            
#. Create the following "imageset-config.yaml" file. In my file below I'm
   mirroring OCP v4.12. I've also added some additional operators and images.

   .. important:: Be sure path in imageURL (line 5)  matches the path assigned for "quayRoot".

   .. code-block:: bash
      :emphasize-lines: 5

      kind: ImageSetConfiguration
      apiVersion: mirror.openshift.io/v1alpha2
      storageConfig:
        registry:
          imageURL: mirror.lab.local:8443/mirror/ocp4
          skipTLS: false
      mirror:
        platform:
          channels:
          - name: stable-4.12
            type: ocp
        operators:
        - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.12
          packages:
          - name: local-storage-operator
          - name: odf-operator
          - name: sriov-network-operator
        additionalImages:
        - name: registry.redhat.io/ubi8/ubi:latest
        - name: registry.redhat.io/ubi9/ubi:latest
        helm: {}

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
