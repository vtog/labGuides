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
      tar -xzvf mirror-registry-2.0.1.tar.gz -C ~/mirror-registry/
      tar -xzvf oc-4.16.8-linux.tar.gz -C ~/.local/bin
      tar -xzvf oc-mirror.rhel9.tar.gz -C ~/.local/bin
      chmod +x ~/.local/bin/oc-mirror
      rm ~/.local/bin/README.md
      cd ~/mirror-registry

#. Create the target directory for the new registry. In my lab I'm using
   "/mirror".

   .. code-block:: bash

      sudo mkdir /mirror

#. Identify and create the **Hostname** and **Directory** session variables. In
   my case I'm using the following for my lab:

   .. important:: For "quayHostname" be sure to use a name that can be resolved
      via DNS or the local hosts file. The installer will use that name to
      validate the service.

   .. important:: With v2 "pgStorage" is replaced with "sqliteStorage".

   .. note:: The "ocp4" directory in "/mirror" will be created by the installer.

   .. code-block:: bash

      cat << EOF > ./variables

      export quayHostname="mirror.lab.local"
      export quayRoot="/mirror/ocp4"
      export quayStorage="/mirror/ocp4"
      export sqliteStorage="/mirror/ocp4"
      export initPassword="password"
      EOF

      source ./variables

Create Local Registry
---------------------

#. Run the following command to install the registry pods as root.

   .. important:: The registry services will be run as root. You can see the
      pods with ``sudo podman ps``

   .. warning:: Installing as "root" will force IPv4 only listener.

   .. tip:: The registry uses port 8443 by default. This can be changed by
      adding :port to $quayHostname when installing. Be sure to add that port
      in every subsequent step.

   .. code-block:: bash

      sudo ./mirror-registry install --quayHostname $quayHostname --quayRoot $quayRoot \
      --quayStorage $quayStorage --sqliteStorage $sqliteStorage --initPassword $initPassword

   If ran correctly should see a similar ansible recap.

   .. image:: ./images/mirror-reg-install.png

   .. tip:: Upgrade running registry

      .. code-block:: bash

         sudo ./mirror-registry upgrade --quayHostname $quayHostname --quayRoot $quayRoot \
         --quayStorage $quayStorage --sqliteStorage $sqliteStorage

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
      --sqliteStorage $sqliteStorage

Mirror Images to Local Registry (v2)
------------------------------------

.. important:: This section is now based on oc-mirror **v2** released with
   v4.18.

#. Before mirroring images we need a copy of your Red Hat "Pull Secret" and update
   it with the local mirror information. If you haven't done so download it here:
   `your pull secret <https://console.redhat.com/openshift/install/pull-secret>`_

#. Convert and copy pull-secret.txt to ~/.docker/config.json

   .. attention:: You may need to install "jq" for this step.

   .. code-block:: bash

      cd ~
      mkdir ~/.docker
      cat ./pull-secret.txt | jq . > ~/.docker/config.json

#. Generate the base64-encoded user name and password for mirror registry.

   .. note:: My registry username and password are "init" and "password".

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

#. Create the following ImageSetConfig yaml files. In these examples I'm
   using seperate files for each channel. You could combine them but I
   found it easier to manage with speration. This also includes an example of
   some additional images I find useful.

   .. tip:: **"graph: true"** mirror's the graph data to the disconnected
      registry. This information enables the disconnected cluster, via the
      update service operator, to show a visual representation of the available
      upgrades.

   .. tip:: **"shortestPath: true"** instructs the oc mirror command to only pull
      the required version to upgrade from one version to the next. It will
      prune any unneeded version.

   .. code-block:: yaml
      :caption: ImageSetConfiguration **4.16** yaml
      :emphasize-lines: 1,8,10,11,15,43,46

      kind: ImageSetConfiguration
      apiVersion: mirror.openshift.io/v2alpha1
      mirror:
        platform:
          architectures:
          - "amd64"
          channels:
          - name: stable-4.16
            type: ocp
            minVersion: 4.16.40
            maxVersion: 4.16.40
            shortestPath: true
          graph: true
        operators:
        - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.16
          packages:
          - name: advanced-cluster-management
          - name: cincinnati-operator
          - name: kubernetes-nmstate-operator
          - name: kubevirt-hyperconverged
          - name: local-storage-operator
          - name: lvms-operator
          - name: metallb-operator
          - name: multicluster-engine
          - name: nfd
          - name: odf-operator
          - name: cephcsi-operator
          - name: mcg-operator
          - name: ocs-client-operator
          - name: ocs-operator
          - name: odf-csi-addons-operator
          - name: odf-dependencies
          - name: odf-multicluster-orchestrator
          - name: odf-prometheus-operator
          - name: recipe
          - name: rook-ceph-operator
          - name: openshift-gitops-operator
          - name: ptp-operator
          - name: quay-operator
          - name: skupper-operator
          - name: sriov-network-operator
          - name: topology-aware-lifecycle-manager
        - catalog: registry.redhat.io/redhat/certified-operator-index:v4.16
          packages:
          - name: gpu-operator-certified
        additionalImages:
        - name: registry.redhat.io/openshift4/ose-cluster-node-tuning-rhel9-operator:v4.16
        - name: registry.redhat.io/openshift4/ztp-site-generate-rhel8:v4.16

   .. code-block:: yaml
      :caption: ImageSetConfiguration **4.17** yaml
      :emphasize-lines: 1,8,10,11,15,43,46

      kind: ImageSetConfiguration
      apiVersion: mirror.openshift.io/v2alpha1
      mirror:
        platform:
          architectures:
          - "amd64"
          channels:
          - name: stable-4.17
            type: ocp
            minVersion: 4.17.30
            maxVersion: 4.17.30
            shortestPath: true
          graph: true
        operators:
        - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.17
          packages:
          - name: advanced-cluster-management
          - name: cincinnati-operator
          - name: kubernetes-nmstate-operator
          - name: kubevirt-hyperconverged
          - name: local-storage-operator
          - name: lvms-operator
          - name: metallb-operator
          - name: multicluster-engine
          - name: nfd
          - name: odf-operator
          - name: cephcsi-operator
          - name: mcg-operator
          - name: ocs-client-operator
          - name: ocs-operator
          - name: odf-csi-addons-operator
          - name: odf-dependencies
          - name: odf-multicluster-orchestrator
          - name: odf-prometheus-operator
          - name: recipe
          - name: rook-ceph-operator
          - name: openshift-gitops-operator
          - name: ptp-operator
          - name: quay-operator
          - name: skupper-operator
          - name: sriov-network-operator
          - name: topology-aware-lifecycle-manager
        - catalog: registry.redhat.io/redhat/certified-operator-index:v4.17
          packages:
          - name: gpu-operator-certified
        additionalImages:
        - name: registry.redhat.io/openshift4/ose-cluster-node-tuning-rhel9-operator:v4.17
        - name: registry.redhat.io/openshift4/ztp-site-generate-rhel8:v4.17

   .. code-block:: yaml
      :caption: ImageSetConfiguration **4.18** yaml
      :emphasize-lines: 1,8,10,11,15,43,46

      kind: ImageSetConfiguration
      apiVersion: mirror.openshift.io/v2alpha1
      mirror:
        platform:
          architectures:
          - "amd64"
          channels:
          - name: stable-4.18
            type: ocp
            minVersion: 4.18.13
            maxVersion: 4.18.13
            shortestPath: true
          graph: true
        operators:
        - catalog: registry.redhat.io/redhat/redhat-operator-index:v4.18
          packages:
          - name: advanced-cluster-management
          - name: cincinnati-operator
          - name: kubernetes-nmstate-operator
          - name: kubevirt-hyperconverged
          - name: local-storage-operator
          - name: lvms-operator
          - name: metallb-operator
          - name: multicluster-engine
          - name: nfd
          - name: odf-operator
          - name: cephcsi-operator
          - name: mcg-operator
          - name: ocs-client-operator
          - name: ocs-operator
          - name: odf-csi-addons-operator
          - name: odf-dependencies
          - name: odf-multicluster-orchestrator
          - name: odf-prometheus-operator
          - name: recipe
          - name: rook-ceph-operator
          - name: openshift-gitops-operator
          - name: ptp-operator
          - name: quay-operator
          - name: skupper-operator
          - name: sriov-network-operator
          - name: topology-aware-lifecycle-manager
        - catalog: registry.redhat.io/redhat/certified-operator-index:v4.18
          packages:
          - name: gpu-operator-certified
        additionalImages:
        - name: registry.redhat.io/openshift4/ose-cluster-node-tuning-rhel9-operator:v4.18
        - name: registry.redhat.io/openshift4/ztp-site-generate-rhel8:v4.18

   .. code-block:: yaml
      :caption: ImageSetConfiguration **additional images** yaml
      :emphasize-lines: 1,4

      kind: ImageSetConfiguration
      apiVersion: mirror.openshift.io/v2alpha1
      mirror:
        additionalImages:
        - name: registry.redhat.io/ubi8/ubi:latest
        - name: registry.redhat.io/ubi9/ubi:latest
        - name: registry.redhat.io/ubi9/httpd-24:latest
        - name: registry.redhat.io/ubi9/nginx-122:latest
        - name: registry.redhat.io/rhel8/support-tools:latest
        - name: registry.redhat.io/rhel9/support-tools:latest
        - name: registry.redhat.io/openshift4/dpdk-base-rhel8:latest
        - name: ghcr.io/k8snetworkplumbingwg/sriov-network-device-plugin:latest
        - name: quay.io/openshift-scale/etcd-perf:latest
        - name: docker.io/centos/tools:latest
        - name: docker.io/f5devcentral/f5-hello-world:latest
        - name: docker.io/library/httpd:latest
        - name: docker.io/library/nginx:latest

   .. tip:: To discover operators by their package name, applicable channels,
      and versions use the following commands.

      .. code-block:: bash

         # List ALL available operators
         oc mirror list operators --catalog registry.redhat.io/redhat/redhat-operator-index:v4.16

         # List package specific inormation for an operator
         oc mirror list operators --package sriov-network-operator --catalog registry.redhat.io/redhat/redhat-operator-index:v4.16

#. Mirror images to registry.

   With oc-mirror v2 we have the option to mirror to disk first then mirror to
   registry. It is possible to mirror directly to the registry as was the
   default with v1 but I prefer the two step method. For disconnected
   environments this is the best and only option.

   .. note:: Be patient! Each step of the process will take a lot of time.

   .. tip:: The process of mirroring to disk will overwrite the cluster
      resources directory with each attempt. To include the previous results
      use the "--since" switch.

   .. important:: If you see missing images/errors at the end of each step,
      re-run the oc-mirror command.

   A. Mirror-to-Disk.

      .. code-block:: bash

         oc mirror --v2 -c ./imageset-config.yaml --since 2025-04-20 file://<directory_name>

      .. image:: ./images/mirror-results.png

      .. tip:: I created the following script to simplify the command:

         .. code-block:: bash

            #!/bin/bash

            OCPV=4.18

            echo "Mirroring $OCPV based on ./isc-$OCPV.yaml"
            echo
            oc mirror --v2 -c ./isc-$OCPV.yaml --since 2025-04-20 file:///mirror/oc-mirror/$OCPV

   #. Disk-to-Mirror.

      .. code-block:: bash

         oc mirror --v2 -c ./imageset-config.yaml --from file://<directory_name> docker://$quayHostname:8443

      .. image:: ./images/mirror-results2.png

      .. tip:: I created the following script to simplify the command:

         .. code-block:: bash

            #!/bin/bash

            OCPV=4.18

            echo "Mirroring $OCPV based on ./isc-$OCPV.yaml"
            echo
            oc mirror --v2 -c ./isc-$OCPV.yaml --from file:///mirror/oc-mirror/$OCPV docker://$quayHostname:8443

#. Make note of the information upon completion. Supporting yaml files can be
   found in "<directory_name>/working-dir/cluster-resources". These files will
   be applied to your running cluster.

#. Connect and login to your mirror: `<https://$quayHostname:8443>`_
   You should see something similar to the following:

   .. image:: ./images/mirror-images.png

Delete Images from Local Registry (v2)
--------------------------------------

With v2 the process no longer auto purges the older files. You have to use the
following two step process.

#. Delete phase 1 (generate)

   .. code-block:: bash

      oc mirror delete --v2 -c ./delete-isc.yaml --generate --workspace file://<directory_name> docker://$quayHostname:8443

#. Delete phase 2 (delete)

   .. code-block:: bash

      oc mirror delete --v2 --delete-yaml-file <directory_name>/working-dir/delete/delete-images.yaml docker://$quayHostname:8443

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

#. Create configmap of quay-rootCA.

   .. code-block:: bash

      oc create configmap registry-config --from-file=$quayHostname..8443=$quayRoot/quay-rootCA/rootCA.pem -n openshift-config

#. Add quay-rootCA to cluster.

   .. code-block:: bash

      oc patch --type merge images.config.openshift.io/cluster --patch '{"spec":{"additionalTrustedCA":{"name":"registry-config"}}}'

#. Apply the YAML files from the results directory to the cluster.

   .. note:: Everytime you successfully run "oc mirror" a "results" dir is
      created.

   .. important:: These results are not cumulative. They do NOT include the
      previously succsessful result. Its VERY important to manaully combine
      this information by diffing the old and new file. Without doing this the
      running cluster will be missing references which are required to install
      and maintain operators and images.

   .. code-block:: bash

      oc apply -f <directory_name>/working-dir/cluster-resources/

#. For disconnected upgrades via the "Openshift Update Service" (next section)
   the "release-signatures" will need to be applied to the cluster.

   .. important:: Disconnected upgrades will NOT work without this step.

   .. code-block:: bash

      oc apply -f <directory_name>/working-dir/cluster-resources/signature-configmap.yaml

#. The ability to install operators from the local mirror requires the default
   operator hub to be disabled.

   .. code-block:: bash

      oc patch OperatorHub cluster --type json -p '[{"op": "add", "path": "/spec/disableAllDefaultSources", "value": true}]'

   .. attention:: Any change to the operator list requires the "CatalogSource"
      to be updated. To do so run "oc remove" and "oc create" of the
      "CatalogSource".
