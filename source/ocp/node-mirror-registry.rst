Node Mirror & Registry
======================

In a disconnected environment you might not always have the option to deploy a
registry and mirror on dedicated server. This guide will walk through the
process of using one or more nodes running in an OpenShift cluster.

Prerequisites
-------------

#. Download the following files and copy to the destination cluster node.

   `Openshift Client <https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/openshift-client-linux.tar.gz>`_

   `Mirror Registry for OpenShift <https://developers.redhat.com/content-gateway/rest/mirror/pub/openshift-v4/clients/mirror-registry/latest/mirror-registry.tar.gz>`_

   `Openshift Client Mirror Plugin <https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/oc-mirror.tar.gz>`_

   `Your Pull Secret <https://console.redhat.com/openshift/install/pull-secret>`_

   .. attention:: These links point to the most recent versions. Typically
      you'll want a specific version. You can find those here:

      `<https://access.redhat.com/downloads/content/290/>`_

#. On a "connected" workstation extract and setup "Openshift Client" and
   "Mirror Plugin".

   .. code-block:: bash

      mkdir -p ~/.local/bin
      tar -xzvf openshift-client-linux.tar.gz -C ~/.local/bin/
      tar -xzvf oc-mirror.tar.gz -C ~/.local/bin/
      chmod +x ~/.local/bin/oc-mirror
      rm ~/.local/bin/README.md

#. Convert your "pull-secret.txt" to json format.
   
   .. attention:: You may need to install "jq" for this step.

   .. code-block:: bash

      cd ~
      cat ./pull-secret.txt | jq . > ./pull-secret.json

#. Copy "pull-secret.json" to ~/.docker and rename "config.json".

   .. code-block:: bash
   
      mkdir ~/.docker   
      cp ./pull-secret.json ~/.docker/config.json

#. Create the following "imageset-config.yaml" file. In the content below I'm
   mirroring OCP v4.12, more specifically only v4.12.5. I've also added some
   additional operators.

   .. attention:: Be sure to update the mirror-platform-channel and operators
      to your specific version and package requirements.

   .. code-block:: yaml
      :emphasize-lines: 6-8,10

      kind: ImageSetConfiguration
      apiVersion: mirror.openshift.io/v1alpha2
      mirror:
        platform:
          channels:
            - name: stable-4.12
              minVersion: 4.12.5
              maxVersion: 4.12.5
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
        additionalImages:
          - name: registry.redhat.io/rhel8/support-tools:latest
          - name: registry.redhat.io/rhel9/support-tools:latest
          - name: registry.redhat.io/openshift4/performance-addon-operator-must-gather-rhel8:v4.12
        helm: {}

   .. tip:: To discover operators by their package name, applicable channels,
      and versions use the following commands. This information can be used to
      update the packages list in the "imageset-config.yaml" file.

      .. code-block:: bash

         # List ALL available operators
         oc mirror list operators --catalog registry.redhat.io/redhat/redhat-operator-index:v4.12

         # List package specific inormation for an operator
         oc mirror list operators --package sriov-network-operator --catalog registry.redhat.io/redhat/redhat-operator-index:v4.12

#. Mirror "imageset" from external mirror to a local file.

   .. important:: This command needs to be run from a **internet connected
      workstation.**

   .. code-block:: bash

      oc mirror --config=./imageset-config.yaml file://<path_to_dir>

   .. note:: Be patient this process will take some time to download all the
      requested images.

#. Successful completion of the previous step should create a new file named,
   ``mirror_seq1_000000.tar``. Copy this file to the destination node.

Create Local Host Mirror Registry
---------------------------------

#. SSH to the target node and run the following commands to place the
   binaries in their respective directories.

   .. code-block:: bash

      mkdir -p ~/.local/bin
      mkdir -p ~/mirror/ocp4
      tar -xzvf mirror-registry.tar.gz -C ~/mirror/
      tar -xzvf openshift-client-linux.tar.gz -C ~/.local/bin/
      tar -xzvf oc-mirror.tar.gz -C ~/.local/bin/
      chmod +x ~/.local/bin/oc-mirror
      rm ~/.local/bin/README.md
      mkdir -p ~/.kube
      sudo cp /etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/node-kubeconfigs/localhost.kubeconfig ~/.kube/config
      sudo chown core:core ~/.kube/config
      sudo chmod 644 /etc/resolv.conf
      cd ~/mirror

#. Identify and create the **Hostname** and **Directory** session variables.
   For example my lab uses the following:

   .. important:: For "quayHostname" be sure to use a name that can be resolved
      via DNS or the local hosts file. The installer will use that name to
      validate the service.

   .. code-block:: bash

      quayHostname="host31.ocp2.lab.local"
      quayRoot="/home/core/mirror/ocp4"
      quayStorage="/home/core/mirror/ocp4"
      pgStorage="/home/core/mirror/ocp4"
      initPassword="password"

#. Run the following command to install the registry.

   .. code-block:: bash

      ./mirror-registry install --quayHostname $quayHostname --quayRoot $quayRoot \
        --quayStorage $quayStorage --pgStorage $pgStorage --initPassword $initPassword

   If ran correctly should see a similar ansible recap.

   .. image:: ./images/mirror-reg-install.png

#. Copy newly created root CA and update the trust.

   .. code-block:: bash

      sudo cp /home/core/mirror/ocp4/quay-rootCA/rootCA.pem /etc/pki/ca-trust/source/anchors/quayCA.pem
      sudo update-ca-trust extract

#. Test mirror availability via cli.

   .. code-block:: bash

       podman login -u init -p password $quayHostname:8443

   .. hint:: Use the "\-\-tls-verify=false" if not adding the rootCA to the trust.

#. Access mirror via browser at `<https://node_IP:8443>`_

   .. hint:: Username = "init" / Password = "password"

.. tip:: If needed, the following command will uninstall the registry.

   .. code-block:: bash

      ./mirror-registry uninstall --quayRoot $quayRoot --quayStorage $quayStorage

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
          "host31.ocp2.lab.local:8443": {
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
            
#. Mirror the "local image tar ball" to the "local mirror"

   .. note:: This file was created and copied to this node in the pre-req
      section.

   .. code-block:: bash

      oc mirror --from=./mirror_seq1_000000.tar docker://$quayHostname:8443

#. Connect and login to your mirror: `<https://host31.ocp2.lab.local:8443>`_
   You should see something similar to the following:

   .. note:: If local DNS doesn't have a record for host31, the IP can be used
      to test the registry.

   .. image:: ./images/mirror-images.png

#. Apply the YAML files from the results directory to the cluster.

   .. important:: Only do this for first Node hosting registry/mirror. If
      adding additional Node redundancy, skip to "Adding Registry & Mirror
      Redundancy" section.

   .. code-block:: bash

      oc apply -f ./oc-mirror-workspace/results-xxxxxxxxxx/

#. The ability to install operators from the local mirror requires the default
   operator hub sources to be disabled.

   .. code-block:: bash

      oc patch OperatorHub cluster --type json -p '[{"op": "add", "path": "/spec/disableAllDefaultSources", "value": true}]'

   .. attention:: Any update to the operator list requires the "CatalogSource"
      to be updated. Delete and recreate the object.

Update Cluster for local registry
---------------------------------

#. Extract OCP pull-secret. A new local file ``.dockerconfigjson`` is created.

   .. code-block:: bash

      oc extract secret/pull-secret -n openshift-config --confirm --to=.
      cat ./.dockerconfigjson | jq . > ./.dockerconfig.json

#. Update ``.dockerconfig.json`` with local registry credentials.

   .. code-block:: json

      {
        "auths": {
          "host31.ocp2.lab.local:8443": {
            "auth": "aW5pdDpwYXNzd29yZA=="
          }
        }
      }

      
#. Import the new pull-secret.

   .. code-block:: bash

      oc set data secret/pull-secret -n openshift-config --from-file=.dockerconfigjson=.dockerconfig.json

#. Create configmap of quay-rootCA.

   .. code-block:: bash

      oc create configmap registry-config --from-file=$quayHostname..8443=/home/core/mirror/ocp4/quay-rootCA/rootCA.pem -n openshift-config

#. Add quay-rootCA to cluster.

   .. code-block:: bash

      oc patch image.config.openshift.io/cluster --patch '{"spec":{"additionalTrustedCA":{"name":"registry-config"}}}' --type=merge

Adding Registry & Mirror Redundancy
-----------------------------------

For redundancy it's possible to run through these steps for each node in the
cluster. The "trick" is to not over write the previous "mirror" config but
append to them.

#. Append updates to ``./oc-mirror-workspace/results-xxxxxxxxxx/imageContentSourcePolicy.yaml``
   before applying them. In the example below I added both mirrors before
   re-applying the policy.

   .. code-block:: yaml
      
      apiVersion: operator.openshift.io/v1alpha1
      kind: ImageContentSourcePolicy
      metadata:
        labels:
          operators.openshift.org/catalog: "true"
        name: operator-0
      spec:
        repositoryDigestMirrors:
        - mirrors:
          - host31.ocp2.lab.local:8443/rhel8
          - host32.ocp2.lab.local:8443/rhel8
          source: registry.redhat.io/rhel8
        - mirrors:
          - host31.ocp2.lab.local:8443/redhat
          - host32.ocp2.lab.local:8443/redhat
          source: registry.redhat.io/redhat
        - mirrors:
          - host31.ocp2.lab.local:8443/container-native-virtualization
          - host32.ocp2.lab.local:8443/container-native-virtualization
          source: registry.redhat.io/container-native-virtualization
        - mirrors:
          - host31.ocp2.lab.local:8443/odf4
          - host32.ocp2.lab.local:8443/odf4
          source: registry.redhat.io/odf4
        - mirrors:
          - host31.ocp2.lab.local:8443/rhceph
          - host32.ocp2.lab.local:8443/rhceph
          source: registry.redhat.io/rhceph
        - mirrors:
          - host31.ocp2.lab.local:8443/openshift4
          - host32.ocp2.lab.local:8443/openshift4
          source: registry.redhat.io/openshift4
      ---
      apiVersion: operator.openshift.io/v1alpha1
      kind: ImageContentSourcePolicy
      metadata:
        name: release-0
      spec:
        repositoryDigestMirrors:
        - mirrors:
          - host31.ocp2.lab.local:8443/openshift/release
          - host32.ocp2.lab.local:8443/openshift/release
          source: quay.io/openshift-release-dev/ocp-v4.0-art-dev
        - mirrors:
          - host31.ocp2.lab.local:8443/openshift/release-images
          - host32.ocp2.lab.local:8443/openshift/release-images
          source: quay.io/openshift-release-dev/ocp-release

#. With ``./oc-mirror-workspace/results-xxxxxxxxxx/catalogSource-redhat-operator-index.yaml``
   a new object for each mirror will need to be created. Update the "name" by
   appending the node-name to the end of the string for each mirror before
   creating the object.

   .. code-block:: yaml
      :emphasize-lines: 4
      
      apiVersion: operators.coreos.com/v1alpha1
      kind: CatalogSource
      metadata:
        name: redhat-operator-index-host32
        namespace: openshift-marketplace
      spec:
        image: host32.ocp2.lab.local:8443/redhat/redhat-operator-index:v4.12
        sourceType: grpc

#. Just like before we'll need to append the new registry to the pull-secret.
   Use previous instructions to "extract" and "set" the pull-secret.

   .. code-block:: json
      :emphasize-lines: 3, 6

      {
        "auths": {
          "host31.ocp2.lab.local:8443": {
            "auth": "aW5pdDpwYXNzd29yZA=="
          },
          "host32.ocp2.lab.local:8443": {
            "auth": "aW5pdDpwYXNzd29yZA=="
          }
        }
      }

#. Append the registry-config configmap with the new CA.

   .. code-block:: yaml
      :emphasize-lines: 2, 6

      oc edit configmap registry-config -n openshift-config

      data:
        host31.ocp2.lab.local..8443: |
          -----BEGIN CERTIFICATE-----
          MIIDxjCCAq6gAwIBAgIUYmcQxIY2...
          -----END CERTIFICATE-----
        host32.ocp2.lab.local..8443: |
          -----BEGIN CERTIFICATE-----
          MIIDxjCCAq6gAwIBAgIUVwvE92Vp...
          -----END CERTIFICATE-----

