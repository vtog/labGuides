Adding a New Node to the Cluster
================================

These steps are based on Red Hat documentation. For a deeper understand of each
step see the following URL:
`Adding worker nodes to single-node OpenShift clusters manually <https://docs.openshift.com/container-platform/4.12/nodes/nodes/nodes-sno-worker-nodes.html#sno-adding-worker-nodes-to-single-node-clusters-manually_add-workers>`_

.. note:: I tested this on 4.12, 4.13, and 4.14.

.. important:: Exactly three control plane nodes must be used for all
   production deployments.

Control or Worker Node
----------------------

Steps to manually add a new **node** to an OpenShift cluster. These steps allow
for the addition of a new master or worker node, depending on how you set the
"NODE_TYPE" variable.

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

      curl -k https://mirror.openshift.com/pub/openshift-v4/clients/ocp/$OCP_VERSION/openshift-install-linux.tar.gz > openshift-install-linux.tar.gz

   Extract the installer

   .. code-block:: bash

      tar -xzvf openshift-install-linux.tar.gz

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

Back-Up ETCD
------------

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

Clean-Up ETCD
-------------

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

Associate Node with MachineSet
------------------------------

After adding the new node you'll notice the new node is up and "Ready" for use
but doesn't match the initial nodes in the cluster. The original nodes are part
of a MachineSet and associated with bare metal host objects.

.. note:: In older version of OCP the Node Overview via the console will show
   errors.

The following creates and associates the required objects for the new node and
resolves any console errors.

#. Log in to the local OCP console.

#. Copy the MAC address of the newly created node to notepad.

#. Go to :menuselection:`Compute --> MachineSets`

   A. Edit the "worker" MachineSet
   #. Increase the "Desired count" by +1

#. Go To :menuselection:`Compute --> Machines` and copy the Name of newly
   created machine to notepad.

#. Go to :menuselection:`Compute --> Bare Metal Hosts`

   A. Click :menuselection:`Add Host --> New from Dialog`
   #. Add Name (ex. worker3)
   #. Add Boot MAC Address (saved earlier when creating node step 2)
   #. Disable "Enable power management"
   #. Click Create

#. Modify the newly created Bare Metal Hosts.

   A. Before editing new object, copy "spec" section from an older BMH object.

      .. code-block:: yaml
         :emphasize-lines: 9, 19

         spec:
           hardwareProfile: unknown
           automatedCleaningMode: metadata
           online: true
           userData:
             name: master-user-data-managed
             namespace: openshift-machine-api
           bootMode: legacy
           bootMACAddress: '52:54:00:f4:16:24'
           bmc:
             address: ''
             credentialsName: ''
           customDeploy:
             method: install_coreos
           externallyProvisioned: true
           consumerRef:
             apiVersion: machine.openshift.io/v1beta1
             kind: Machine
             name: mtu1-29n7r-master-2
             namespace: openshift-machine-api

   #. Edit new BMH object
   #. Click YAML tab
   #. Replace "spec" section with older BMH "spec" previously copied.
   #. Be sure to use the new nodes "bootMACAddress:" saved in step 2 and
      "consumerRef/name:" saved in step 4.
   #. Click Save
   #. Before exiting copy the "uid" to notepad.

#. Go to :menuselection:`Compute --> Nodes`

   A. Select/edit new Node
   #. Click YAML tab
   #. Add following annotation

      .. code-block:: yaml

         machine.openshift.io/machine: openshift-machine-api/<new machine name created in step 4>

   #. Replace "spec" section with following "spec"

      .. danger:: Making a mistake here can be catastrophic. You can't update
         or change this "spec" once saved. Only option is to remove node and
         rebuild it.

      .. code-block:: yaml

         spec:
           providerID: >-
             baremetalhost:///openshift-machine-api/<NODE_NAME>/<UID>

   #. Click Save
