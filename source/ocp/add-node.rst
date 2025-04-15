Adding a New Node to the Cluster
================================

Option 1 (Preferred)
^^^^^^^^^^^^^^^^^^^^

This option uses BareMetalHost and BMC for provisioning. Three objects need to
be created:

- Secret (BMC authentication)
- Secret (NMState config)
- BareMetalHost

.. note:: All objects are created in the "openshift-machine-api" namespace.

#. Create the BMC authentication secret.

   .. important:: The username and password are generated with base64.

      .. code-block:: bash

         echo -n 'kni' | base64 -w0

   .. code-block:: yaml
      :emphasize-lines: 2,4,5,8,9

      cat << EOF > ./host34-secret.yaml
      apiVersion: v1
      kind: Secret
      metadata:
        name: bmc-secret-host34
        namespace: openshift-machine-api
      type: Opaque
      data:
        password: a25p
        username: a25p
      EOF

#. Create the NMState config secret.

   .. important:: Adjust nmstate interface config for the new node.

   .. code-block:: yaml
      :emphasize-lines: 2,4,5,10-12,14,15,18,19,24,25,31,33,37,38

      cat << EOF > ./host34-nmstate.yaml
      apiVersion: v1
      kind: Secret
      metadata:
        name: bmc-secret-nmstate-host34
        namespace: openshift-machine-api
      type: Opaque
      stringData:
       nmstate: |
         interfaces:
           - name: enp1s0
             type: ethernet
             mtu: 9000
             state: up
           - name: enp1s0.132
             type: vlan
             state: up
             vlan:
               base-iface: enp1s0
               id: 132
             ipv4:
               enabled: true
               dhcp: false
               address:
                 - ip: 192.168.132.34
                   prefix-length: 24
             ipv6:
               enabled: false
         dns-resolver:
           config:
             search:
               - lab.local
             server:
               - 192.168.1.68
         routes:
           config:
             - destination: 0.0.0.0/0
               next-hop-address: 192.168.132.1
               next-hop-interface: enp1s0.132
               table-id: 254
      EOF

#. Create the BareMetalHost.

   .. important:: The "credentialsName" and "preprovisioningNetworkDataName"
      need to match the names used in the previous two steps.

   .. code-block:: yaml
      :emphasize-lines: 2,4,5,8,10-12,14,15

      cat << EOF > ./host34-baremetal.yaml
      apiVersion: metal3.io/v1alpha1
      kind: BareMetalHost
      metadata:
        name: host34.lab.local
        namespace: openshift-machine-api
      spec:
        online: true
        bootMACAddress: 52:54:00:f4:16:34
        bmc:
          address: redfish-virtualmedia+http://192.168.1.72:8000/redfish/v1/Systems/f9f66728-9743-4568-b6b9-ef7b44ba65c8
          credentialsName: bmc-secret-host34
          disableCertificateVerification: true
        rootDeviceHints:
          deviceName: "/dev/vda"
        preprovisioningNetworkDataName: bmc-secret-nmstate-host34
      EOF

#. Once the files are modified and ready create them:

   .. code-block:: bash

      oc create -f ./

#. Follow the creation progress. The BareMetalHost should show "available" when
   ready.

   .. note:: Your metal3-baremenatel-operator pod will have a different hash.

   .. code-block:: bash

      oc logs metal3-baremetal-operator-8749b7fd5-krgw6 -n openshift-machine-api --follow

      # and/or

      ssh core@host34 journalctl -f

   .. code-block:: bash

      oc get bmh -n openshift-machine-api

#. From the OpenShift console confirm new BMH is "Available:

   Go to :menuselection:`Compute --> Bare Metal Hosts`

   .. image:: ./images/bmh-available.png

#. From the OpenShift console modify the MachineSet to add the "available" node
   to the cluster:

   Go to :menuselection:`Compute --> MachineSets`

   .. image:: ./images/machineset-worker.png

   .. image:: ./images/machineset-adjust-count.png

   .. tip:: You can make this modification via the command line:

      .. code-block:: bash

         oc scale --replicas=<worker_nodes> machineset <machineset> -n openshift-machine-api

         # oc scale --replicas=1 machineset ocp3-d5zw7-worker-0 -n openshift-machine-api

Option 2 (Manual)
^^^^^^^^^^^^^^^^^

These steps are based on Red Hat documentation. For a deeper understand of each
step see the following URL:
`Adding worker nodes to single-node OpenShift clusters manually <https://docs.openshift.com/container-platform/4.12/nodes/nodes/nodes-sno-worker-nodes.html#sno-adding-worker-nodes-to-single-node-clusters-manually_add-workers>`_

.. note:: I've tested this on 4.12 through 4.18.

.. warning:: Exactly three control plane nodes must be used for all
   production deployments prior to 4.18. With 4.18 you can have more then
   three.

.. important:: These steps allow for the addition of a new master or worker
   node depending on how you set the "NODE_TYPE" variable.

#. Set the environment variables. Be sure to use the variables that match your
   running version and architecture. Specify "master" or "worker" depending on
   the desired node type.

   .. code-block:: bash

      OCP_VERSION=4.14.1
      ARCH=x86_64
      NODE_TYPE=worker

#. Extract the ignition file.

   .. code-block:: bash

      oc extract -n openshift-machine-api secret/$NODE_TYPE-user-data-managed --keys=userData --to=- > $NODE_TYPE.ign

   .. important:: Place this file on a web server reachable from the control-plane network.

#. Create a new igniton file "new-$NODE_TYPE.ign" that includes a reference to
   the original "$NODE_TYPE.ign" and an additional instruction that the
   coreos-installer program uses to populate the /etc/hostname file on the new
   host.

   .. code-block:: yaml
      :emphasize-lines: 8,18

      cat << EOF > ./new-$NODE_TYPE.ign
      {
        "ignition":{
          "version":"3.2.0",
          "config":{
            "merge":[
              {
                "source":"http://192.168.1.72/$NODE_TYPE.ign"
              }
            ]
          }
        },
        "storage":{
          "files":[
            {
              "path":"/etc/hostname",
              "contents":{
                "source":"data:,host44.lab.local"
              },
              "mode":420,
              "overwrite":true,
              "path":"/etc/hostname"
            }
          ]
        }
      }
      EOF

   .. important:: Place this file on a web server reachable from the control-plane network.

#. If needed download the OCP installer.

   .. code-block:: bash

      curl -k https://mirror.openshift.com/pub/openshift-v4/clients/ocp/$OCP_VERSION/openshift-install-linux.tar.gz > openshift-install-linux-$OCP_VERSION.tar.gz

   Extract the installer

   .. code-block:: bash

      tar -xzvf openshift-install-linux-$OCP_VERSION.tar.gz

#. Discover the RHCOS ISO URL

   .. code-block:: bash

      ISO_URL=$(./openshift-install coreos print-stream-json | grep location | grep $ARCH | grep iso | cut -d\" -f4)

#. Download the RHCOS ISO

   .. code-block:: bash

      curl -L $ISO_URL -o rhcos-$OCP_VERSION-$ARCH-live.iso

#. Boot the target host from the RHCOS ISO.

#. If not using DHCP or have a custom network config use the RHEL tools to
   configure the network.

#. Check the block devices and "wipe" if needed.

   .. note:: With baremetal hardware it may be necesary to "wipe" the previous
      block device partitions and signatures.

   .. code-block:: bash

      lsblk

   .. code-block:: bash

      sudo wipefs -af /dev/vda

   .. tip:: Be sure to check that all partitions are "wiped" with lsblk. I've
      seen LVM partitions not get removed.

#. Once the network is configured and operational run following command:

   .. attention:: Update the command for your ignition url and block device.

   .. code-block:: bash

      sudo coreos-installer install --copy-network --insecure-ignition --ignition-url=http://192.168.1.72/new-$NODE_TYPE.ign /dev/vda

#. When the install is complete, **reboot** the host.

   .. image:: ./images/coreos-install-complete.png

   .. note:: The machine may reboot more than once.

#. For the new host to join the cluster, several pending csr's will need to be
   approved.

   .. attention:: The csr approval command will need to be run more than once.

   .. code-block:: bash

      oc get csr

   .. code-block:: bash

      oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs --no-run-if-empty oc adm certificate approve

#. After all the csr's are approved, confirm the node was added.

   .. code-block:: bash

      oc get nodes

      oc get mcp

   In my example I added two new nodes, host44 and host45.

   .. image:: ./images/checknewnode.png

Associate Node with MachineSet
------------------------------

After adding the new node you'll notice the new node is up and "Ready" for use
but doesn't match the initial nodes in the cluster. The original nodes are part
of a MachineSet and associated with bare metal host objects.

.. note:: In older version of OCP the Node Overview via the console will show
   errors.

The following creates and associates the required objects for the new node and
resolves any console errors.

#. Set the variables needed to complete steps. Use the node name of the new
   node. In my example "host35.lab.local"

   .. code-block:: bash

      NODENAME=host35.lab.local
      NODEUID=$(oc get nodes $NODENAME --template='{{.metadata.uid}}')

#. From the cli increase the MachineSet by +1.

   .. tip:: Check the current number of replicas first. This will ensure you
      set the replicas to a proper number. The following command will show
      "DESIRED" and "CURRENT".

      .. code-block:: bash

         oc get machinesets -n openshift-machine-api

   .. code-block:: bash

      oc scale --replicas=1 machineset ocp3-d5zw7-worker-0 -n openshift-machine-api

#. Find the name of the newly created Machine. There should be a new name in
   the "Provisioning" phase. Set that name to the variable MACHINENAME.

   .. code-block:: bash

      oc get machines -n openshift-machine-api

      MACHINENAME=$(oc get machines | grep Provisioning | awk '{print $1}')
      MACHINEUID=$(oc get machines $MACHINENAME --template='{{.metadata.uid}}')

#. Add the new BareMetalHost by copy the following yaml and making the necesary
   changes for you node.

   .. note:: Since this node was provsioned externally we need to add the
      "externallyProvisioned: true" switch.

   .. code-block:: yaml
      :emphasize-lines: 1,3,7,13-16,20,25

      cat << EOF > ./$NODENAME-baremetal.yaml
      apiVersion: metal3.io/v1alpha1
      kind: BareMetalHost
      metadata:
        name: $NODENAME
        namespace: openshift-machine-api
      spec:
        architecture: x86_64
        automatedCleaningMode: metadata
        bmc:
          address: redfish-virtualmedia+http://192.168.1.72:8000/redfish/v1/Systems/a3fce101-8d6c-4f74-9145-c8e79415cc84
          credentialsName: bmc-secret-$NODENAME
          disableCertificateVerification: true
        bootMACAddress: 52:54:00:f4:16:35
        consumerRef:
          apiVersion: machine.openshift.io/v1beta1
          kind: Machine
          name: $MACHINENAME
          namespace: openshift-machine-api
        customDeploy:
          method: install_coreos
        online: true
        externallyProvisioned: true
        userData:
          name: worker-user-data-managed
          namespace: openshift-machine-api
      EOF

#. Add the new credentialName Secret for the BareMetalHost.

   .. important:: The username and password are generated with base64.

      .. code-block:: bash

         echo -n 'kni' | base64 -w0

   .. code-block:: yaml
      :emphasize-lines: 3,5,9,10

      cat << EOF > ./$NODENAME-secret.yaml
      apiVersion: v1
      kind: Secret
      metadata:
        name: bmc-secret-$NODENAME
        namespace: openshift-machine-api
      type: Opaque
      data:
        password: a25p
        username: a25p
      EOF

#. Create the new objects.

   .. code-block:: bash

      oc create -f $NODENAME-secret.yaml

      oc create -f $NODENAME-baremetal.yaml

#. Find the new BMH UID

   .. code-block:: bash

      BMHUID=$(oc get bmh $NODENAME --template='{{.metadata.uid}}')

#. Create the Node patch

   .. code-block:: bash

      cat << EOF > ./$NODENAME-patch.yaml
      spec:
        providerID: >-
          baremetalhost:///openshift-machine-api/$NODENAME/$BMHUID
      EOF

#. Modify the node to associate it with the BareMetalHost.

   .. code-block:: bash

      oc patch node $NODENAME -p '{"metadata":{"annotations":{"machine.openshift.io/machine": "openshift-machine-api/'$MACHINENAME'"}}}'

      oc patch node $NODENAME -p '{"spec":{"providerID":"baremetalhost:///openshift-machine-api/'$NODENAME'/'$BMHUID'"}}'

ETCD
^^^^

Back-Up
-------

OpenShift comes with scripts that will backup the etcd state. It's best
practice to backup etcd before removing and replacing a control node.

.. seealso:: `Control plane backup and restore <https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/backup_and_restore/control-plane-backup-and-restore>`_

#. Determine which master node is currently the leader.

   A. Change to the openshift-etcd project

      .. code-block:: bash

         oc project openshift-etcd

   #. List the etcd pods

      .. code-block:: bash

         oc get pods | grep etcd

      .. image:: ./images/getetcdpods.png

   #. RSH into any of the etcd-<node> pods

      .. code-block:: bash

         oc rsh etcd-host41.lab.local

   #. From within that pod run the following command to find the etcd leader.
      Exit pod after noting the current leader. This is where the backup script
      will be run from.

      .. code-block:: bash

         etcdctl endpoint status -w table

      .. image:: ./images/etcdleader.png

#. Connect to the etcd leader node via ssh

   .. code-block:: bash

      ssh core@host41.lab.local

#. Execute the etcd backup script

   .. code-block:: bash

      sudo /usr/local/bin/cluster-backup.sh /home/core/etcd-backup

#. Verify both snapshot_<TIME_STAMP>.db and
   static_kuberesources_<TIME_STAMP>.tar.gz exist. Move files to a safe
   location in the event of failure.

   .. image:: ./images/backupetcd.png

Clean-Up
--------

In the event of a control node failure the failed node must be removed from
etcd. Before starting be sure to follow the previous section backing up etcd.

.. seealso:: `Control plane backup and restore <https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/backup_and_restore/control-plane-backup-and-restore>`_

#. Remove failed node

   .. code-block:: bash

      oc delete node host41.lab.local

#. Confirm removal

   .. code-block:: bash

      oc get nodes

#. Change to the openshift-etcd project

   .. code-block:: bash

      oc project openshift-etcd

#. List the etcd pods

   .. code-block:: bash

      oc get pods | grep etcd

   .. image:: ./images/getetcdpods.png

#. RSH into any of the etcd-<node> pods

   .. code-block:: bash

      oc rsh etcd-host42.lab.local

#. From within that pod run the following command to list the etcd members.
   Note the ID associated with the failed master.

   .. code-block:: bash

      etcdctl member list -w table

   .. image:: ./images/etcdmembers.png

#. Remove the NODE from the etcd database using the ID noted in the previous
   step.

   .. code-block:: bash

      etcdctl member remove <ID>

#. Validate removal. The failing member should no long appear in the member
   list. Exit pod after validating.

   .. code-block:: bash

      etcdctl member list -w table

#. Get and delete the nodes etcd secrets. There should be three of them.

   .. code-block:: bash

      oc get secrets | grep <NODE>

   Delete

   .. code-block:: bash

      oc delete secret etcd-peer-<NODE>
      oc delete secret etcd-serving-<NODE>
      oc delete secret etcd-serving-metrics-<NODE>

#. Add the replacement Node to the cluster using "`Adding a New Node to the
   Cluster <./add-node.html#control-or-worker-node>`_" above.

Verify ETCD
-----------

After adding the new node to the cluster, we need to ensure that the pods are
running and force a redeployment of this etcd member using the etcd operator.

.. seealso:: `Control plane backup and restore <https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/backup_and_restore/control-plane-backup-and-restore>`_

#. Check the etcd operator "AVAILABLE" status is "True". If not you may need to
   wait or troubleshoot the status.

   .. code-block:: bash

      oc get co

#. Change to the openshift-etcd project

   .. code-block:: bash

      oc project openshift-etcd

#. Check all etcd pods have been created

   .. code-block:: bash

      oc get pods | grep etcd

   .. image:: ./images/getetcdpods.png

#. RSH into any of the etcd-<node> pods

   .. code-block:: bash

      oc rsh etcd-host42.lab.local

#. From within that pod run the following command to list the etcd members.

   .. code-block:: bash

      etcdctl member list -w table

#. From within that pod run the following command to view the endpoint status.

   .. code-block:: bash

      etcdctl endpoint status -w table

#. (OPTIONAL) Force redeployment of etcd cluster.

   .. attention:: This is from an older doc and is not necesary. I kept the
      command for reference. It may come in handy if etcd doesn't automagically
      deploy and needs to be "forced".

   .. code-block:: bash

      oc patch etcd cluster -p='{"spec": {"forceRedeploymentReason": "single-master-recovery-'"$( date --rfc-3339=ns )"'"}}' --type=merge
