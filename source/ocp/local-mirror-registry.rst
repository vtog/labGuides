Local Mirror & Registry
=======================

The following Guide will walk through the process of creating a local mirror
and registry for deploying OpenShift on a disconnected network.

Prerequisites
-------------

#. Download the following files and copy to the destination server.

   `Openshift Client <https://mirror.openshift.com/pub/openshift-v4/x86_64/clients/ocp/stable/openshift-client-linux.tar.gz>`_

   `Mirror Registry for OpenShift <https://mirror.openshift.com/pub/cgw/mirror-registry/latest/mirror-registry-amd64.tar.gz>`_

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

      sudo ./mirror-registry install --quayHostname $quayHostname --quayRoot $quayRoot \
      --quayStorage $quayStorage --pgStorage $pgStorage --initPassword $initPassword

   If ran correctly should see a similar ansible recap.

   .. image:: ./images/mirror-reg-install.png

   .. tip:: Upgrade running registry

      .. code-block:: bash

         sudo ./mirror-registry upgrade --quayHostname $quayHostname --quayRoot $quayRoot \
         --quayStorage $quayStorage --pgStorage $pgStorage

#. Copy newly created root CA, update trust, and open firewall port.

   .. code-block:: bash

      sudo cp $quayRoot/quay-rootCA/rootCA.pem /etc/pki/ca-trust/source/anchors/quayCA.pem
      sudo update-ca-trust extract
      sudo firewall-cmd --add-port=8443/tcp --permanent
      sudo firewall-cmd --reload

#. Test mirror availability via cli. The following command should return
   "Login Succeeded!" if everything is working.

   .. code-block:: bash

       podman login -u init -p $initPassword $quayHostname:8443

   .. hint:: Use the "\-\-tls-verify=false" if not adding the rootCA to the trust.

#. Access mirror via browser at `<https://$quayHostname:8443>`_

   .. hint:: Username = "init" / Password = "password"

.. tip:: If something went wrong, the following command will **UNINSTALL** the
   registry.

   .. code-block:: bash

      sudo ./mirror-registry uninstall --quayRoot $quayRoot --quayStorage $quayStorage \
      --pgStorage $pgStorage

Mirror Images to Local Registry
-------------------------------

#. Before mirroring images we need a copy of your Red Hat "Pull Secret" and update
   it with the local mirror information. If you haven't done so download it here:
   `your pull secret <https://console.redhat.com/openshift/install/pull-secret>`_

#. Convert and copy pull-secret.json to ~/.docker and rename config.json

   .. attention:: You may need to install "jq" for this step.

   .. code-block:: bash

      mkdir ~/.docker
      cat ./pull-secret.txt | jq . > ~/.docker/config.json

#. Generate the base64-encoded user name and password for mirror registry.

   .. code-block:: bash

      echo -n 'init:password' | base64 -w0

#. Modify ~/.docker/config.json by adding local mirror information. Use the
   previous steps encoded output for "auth".

   .. attention:: Be sure to replace "$quayHostname:8443" environment variable
      with the real name. For example "mirror.lab.local:8443".

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

#. Create the following "imageset-config.yaml" file. In the example ImageSet
   file below I'm mirroring 4.12.x, 4.13.x and 4.14.x images and operators.
   Plus some additional images I find useful.

   .. attention:: Be sure path in imageURL (line 5) matches the path assigned
      earlier for "quayRoot".

   .. note:: **"graph: true"** mirror's the graph data to the disconnected
      registry. This information enables the disconnected cluster, via the
      update service operator, to show a visual representation of the available
      upgrades.

   .. note:: **"shortestPath: true"** instructs the oc mirror command to only pull
      the required version to upgrade from one version to the next. It will
      prune any unneeded version.

   .. attention:: Be sure to replace "$quayHostname:8443$quayRoot" environment
      variables with the real names. For example imageURL: would be set to
      "mirror.lab.local:8443/mirror/ocp4".

   .. code-block:: yaml
      :emphasize-lines: 5,10,13,14,17,18,21,22,24,39,54

      kind: ImageSetConfiguration
      apiVersion: mirror.openshift.io/v1alpha2
      storageConfig:
        registry:
          imageURL: $quayHostname:8443$quayRoot
          skipTLS: false
      mirror:
        platform:
          channels:
            - name: stable-4.12
              type: ocp
              minVersion: 4.12.34
              shortestPath: true
            - name: stable-4.13
              type: ocp
              minVersion: 4.13.14
              shortestPath: true
            - name: stable-4.14
              type: ocp
              minVersion: 4.14.4
              shortestPath: true
          graph: true
        operators:
          - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.12
            packages:
              - name: advanced-cluster-management
              - name: cincinnati-operator
              - name: kubernetes-nmstate-operator
              - name: kubevirt-hyperconverged
              - name: local-storage-operator
              - name: lvms-operator
              - name: metallb-operator
              - name: multicluster-engine
              - name: odf-operator
              - name: openshift-gitops-operator
              - name: quay-operator
              - name: skupper-operator
              - name: sriov-network-operator
          - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.13
            packages:
              - name: advanced-cluster-management
              - name: cincinnati-operator
              - name: kubernetes-nmstate-operator
              - name: kubevirt-hyperconverged
              - name: local-storage-operator
              - name: lvms-operator
              - name: metallb-operator
              - name: multicluster-engine
              - name: odf-operator
              - name: openshift-gitops-operator
              - name: quay-operator
              - name: skupper-operator
              - name: sriov-network-operator
          - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.14
            packages:
              - name: advanced-cluster-management
              - name: cincinnati-operator
              - name: kubernetes-nmstate-operator
              - name: kubevirt-hyperconverged
              - name: local-storage-operator
              - name: lvms-operator
              - name: metallb-operator
              - name: multicluster-engine
              - name: odf-operator
              - name: openshift-gitops-operator
              - name: quay-operator
              - name: skupper-operator
              - name: sriov-network-operator
        additionalImages:
          - name: registry.redhat.io/ubi8/ubi:latest
          - name: registry.redhat.io/ubi9/ubi:latest
          - name: registry.redhat.io/ubi9/httpd-24:latest
          - name: registry.redhat.io/ubi9/nginx-122:latest
          - name: registry.redhat.io/rhel8/support-tools:latest
          - name: registry.redhat.io/rhel9/support-tools:latest
          - name: registry.redhat.io/openshift4/dpdk-base-rhel8:latest
          - name: registry.redhat.io/openshift4/performance-addon-operator-must-gather-rhel8:v4.12
          - name: registry.redhat.io/openshift4/performance-addon-operator-must-gather-rhel8:v4.13
          - name: registry.redhat.io/openshift4/ose-cluster-node-tuning-operator:v4.12
          - name: registry.redhat.io/openshift4/ose-cluster-node-tuning-operator:v4.13
          - name: registry.redhat.io/openshift4/ose-cluster-node-tuning-operator:v4.14
          - name: registry.redhat.io/openshift4/ose-cluster-node-tuning-rhel9-operator:v4.15
          - name: registry.redhat.io/openshift4/ose-cluster-node-tuning-rhel9-operator:v4.16
          - name: quay.io/openshift/origin-sriov-network-device-plugin:4.12
          - name: quay.io/openshift/origin-sriov-network-device-plugin:4.13
          - name: quay.io/openshift/origin-sriov-network-device-plugin:4.14
          - name: quay.io/openshift-scale/etcd-perf:latest
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

   .. note:: Ran into prunning errors. Tried "--skip-pruning" but not sure that
      was helpful. Last tried "\-\-continue-on-error" and "\-\-ignore-history".
      Noting here for reference.

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

.. attention:: The first 3 steps are only needed when moving a cluster from
   connected to disconnected. If you built the cluster "disconnected" with this
   registry skip to step 4.

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

   .. attention:: This will cause MCP to update all nodes

#. Create configmap of quay-rootCA.

   .. code-block:: bash

      oc create configmap registry-config --from-file=$quayHostname..8443=$quayRoot/quay-rootCA/rootCA.pem -n openshift-config

   .. attention:: This will cause MCP to update all nodes

#. Add quay-rootCA to cluster.

   .. code-block:: bash

      oc patch --type merge images.config.openshift.io/cluster --patch '{"spec":{"additionalTrustedCA":{"name":"registry-config"}}}'

   .. attention:: This will cause MCP to update all nodes

#. Apply the YAML files from the results directory to the cluster.

   .. note:: Everytime you successfully run "oc mirror" a "results" dir is
      created.

   .. important:: These results are not cumulative. They do NOT include the
      previously succsessful result. Its VERY important to manaully combine
      this information by diffing the old and new file. Without doing this the
      running cluster will be missing references which are required to install
      and maintain operators and images.

   .. code-block:: bash

      oc apply -f ./oc-mirror-workspace/results-xxxxxxxxxx/

#. For disconnected upgrades via the "Openshift Update Service" (next section)
   the "release-signatures" will need to be applied to the cluster.

   .. important:: Disconnected upgrades will NOT work without this step.

   .. code-block:: bash

      oc apply -f ./oc-mirror-workspace/results-xxxxxxxxx/release-signatures/

#. The ability to install operators from the local mirror requires the default
   operator hub to be disabled.

   .. code-block:: bash

      oc patch OperatorHub cluster --type json -p '[{"op": "add", "path": "/spec/disableAllDefaultSources", "value": true}]'

   .. attention:: Any change to the operator list requires the "CatalogSource"
      to be updated. To do so run "oc remove" and "oc create" of the
      "CatalogSource".

Upgrade a Disconnected Cluster
------------------------------

The easiest way to update a disconnected cluster is via the cli.

#. From your disconnected registry/mirror, find the release image to upgrade
   to.

   A. Browse to registry, https://mirror.lab.local:8443
   #. Filter Repositories for "release-image" and click Name.
   #. On the left hand side select the "Tags" icon.
   #. Search for the image tag to upgrade to and click the "Fetch Tag" icon.

      .. image:: images/fetch-release-tags.png

   #. In the "Image Format" drop down list select "Podman Pull (by digest)"
      and click the "Copy Command"

      .. image:: images/pull-by-digest.png

#. From the CLI start the upgrade. Use the "\-\-to-image=" switch and the image
   identified in the previous steps.

   .. note:: Be sure to only use the url and release. You can remove "podman
      pull" from the copied content.

   .. code-block:: bash

      oc adm upgrade --to-image=mirror.lab.local:8443/openshift/release-images@sha256:a0ef946ef8ae75aef726af1d9bbaad278559ad8cab2c1ed1088928a0087990b6

Configure Openshift Update Service
----------------------------------

This process is one way to upgrade a disconnected cluster using your local
disconnected registry and the "cincinnati" operator.

#. The Update Service Operator needs the config map to include the key name
   "updateservice-registry" in the registry CA cert. Edit the ConfigMap
   "registry-config" and add the new section using the same local mirror cert.

   .. attention:: This ConfigMap was created in the previous section, steps 4-5.

      .. code-block:: bash

         oc create configmap registry-config --from-file=$quayHostname..8443=$quayRoot/quay-rootCA/rootCA.pem -n openshift-config

         oc patch --type merge images.config.openshift.io/cluster --patch '{"spec":{"additionalTrustedCA":{"name":"registry-config"}}}'

   .. code-block:: bash

      oc edit cm registry-config -n openshift-config

   Add the following highlighted section.

   .. code-block:: yaml
      :emphasize-lines: 7-10

      apiVersion: v1
      data:
        mirror.lab.local..8443: |
          -----BEGIN CERTIFICATE-----
          <Use rootCA.pem from your mirror registry here>
          -----END CERTIFICATE-----
        updateservice-registry: |
          -----BEGIN CERTIFICATE-----
          <Use rootCA.pem from your mirror registry here>
          -----END CERTIFICATE-----
      kind: ConfigMap
      metadata:
        name: registry-config
        namespace: openshift-config

#. Add router-ca to "Proxy" object as a trustedCA.

   .. code-block:: bash

      oc get -n openshift-ingress-operator secret router-ca -o jsonpath="{.data.tls\.crt}" | base64 -d > ca-bundle.crt
      oc create cm router-bundle --from-file=ca-bundle.crt -n openshift-config
      oc edit proxy cluster

   Update the highlighted line.

   .. code-block:: yaml
      :emphasize-lines: 11

      apiVersion: config.openshift.io/v1
      kind: Proxy
      metadata:
        creationTimestamp: "2021-12-21T05:36:05Z"
        generation: 1
        name: cluster
        resourceVersion: "665"
        uid: d2d476ba-c98c-46dd-8130-b85d40d009fb
      spec:
        trustedCA:
          name: "router-bundle"
      status: {}

   .. important:: This change will cause the nodes to cycle through a reboot.
      Before moving to next step wait for the change to apply to all nodes.
      Monitor via "oc get nodes" and/or "oc get mcp"

#. Install the Openshift Update Service Operator from the Web Console. Go to
   :menuselection:`Operators --> OperatorHub` and search for "update".

   .. image:: images/operatorhubupdatesvc.png

#. Select "Openshift Update Service" operator and click install.

#. By default, the “openshift-update-service” namespace will be used. Accept
   the defaults and click “Install”.

#. After install completes click “View Operator”.

#. Select the “Update Service” tab.

#. Click "Create UpdateService".

#. Select "YAML view"

#. Replace the sample yaml with the results from your mirror. The
   "updateService.yaml" can be found at
   "./oc-mirror-workspace/results-xxxxxxxxxx” and should look like the
   following example:

   .. attention:: Every time the registry is updated, this graph-image sha256
      hash will change. This object will have to be updated.

   .. code-block:: yaml

      apiVersion: updateservice.operator.openshift.io/v1
      kind: UpdateService
      metadata:
        name: update-service-oc-mirror
      spec:
        graphDataImage: mirror.lab.local:8443/openshift/graph-image@sha256:2af43ff6160363bec6ab2567738b1a9ed9f3a8129f8b9fd1f09e6f6b675f2e69
        releases: mirror.lab.local:8443/openshift/release-images
        replicas: 2

#. Patch the Cluster Version Operator

   .. code-block:: bash

      NAMESPACE=openshift-update-service
      NAME=update-service-oc-mirror
      POLICY_ENGINE_GRAPH_URI="$(oc -n "${NAMESPACE}" get -o jsonpath='{.status.policyEngineURI}/api/upgrades_info/v1/graph{"\n"}' updateservice "${NAME}")"
      PATCH="{\"spec\":{\"upstream\":\"${POLICY_ENGINE_GRAPH_URI}\"}}"

      oc patch --type merge clusterversion version --patch $PATCH

#. Check :menuselection:`Administration --> Cluster Settings"`. Details should
   display Current version and Update status

   .. image:: images/updatesvcclustersettings.png
