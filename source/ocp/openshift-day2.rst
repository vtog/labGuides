OpenShift Day 2
===============

Schedule Control Nodes
----------------------

#. Enable

   .. code-block:: bash

      oc patch schedulers.config.openshift.io/cluster --type merge -p '{"spec":{"mastersSchedulable":true}}'

#. Disable

   .. code-block:: bash

      oc patch schedulers.config.openshift.io/cluster --type merge -p '{"spec":{"mastersSchedulable":false}}'

Adding Node to Cluster
----------------------

The Assisted Installer has the ability to add Nodes to the cluster but the new
Node is not created in the same way as the original Nodes. The original Nodes
are part of a MachineSet and associated with bare metal host objects. The new
Node shows up as available but the Node Overview via the console shows errors.
After adding the new Node via AI, login in to the local OCP console. The
following creates and associates the required objects for the new Node and
resolves the error from the initial creation.

#. Copy the MAC address of the newly created Node to notepad.

#. Go to :menuselection:`Compute --> MachineSets`

   - Edit the "worker" MachineSet
   - Increase the "Desired count" by +1

#. Go To :menuselection:`Compute --> Machines`

   - Copy the Name of newly created machine to notepad.

#. Go to :menuselection:`Compute --> Bare Metal Hosts`

   - Click :menuselection:`Add Host --> New from Dialog`
   - Add Name (ex. worker3)
   - Add Boot MAC Address (saved earlier when creating Node step 1)
   - Disable "Enable power management"
   - Click Create

#. Modify newly created Bare Metal Hosts
   
   - Before editing new object, copy "spec" section from an older BMH object.

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

   - Edit new BMH object
   - Click YAML tab
   - Replace "spec" section with older BMH "spec" previously copied.
   - Be sure to use the new "Node bootMACAddress" saved in step 1 and
     "consumerRef/name" saved in step 3.
   - Click Save
   - Before exiting copy the "uid" to notepad.

#. Go to :menuselection:`Compute --> Nodes`

   - Select/edit new Node
   - Click YAML tab
   - Add following annotation

     .. code-block:: yaml

        machine.openshift.io/machine: openshift-machine-api/<new machine name created in step 3>

   - Replace "spec" section with following "spec"

     .. code-block:: yaml

        spec:
          providerID: >-
            baremetalhost:///openshift-machine-api/<node_name>/<uid>

   - Click Save

