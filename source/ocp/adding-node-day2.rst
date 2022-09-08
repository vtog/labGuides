Adding Node to Cluster
======================

The Assisted Installer has the ability to add Nodes to the cluster but the new
Node is not created in the same way as the original Nodes. The original Nodes
are part of a MachineSet and associated with bare metal host objects. The new
Node shows up as available but the Node Overview via the console shows errors.
After adding the new Node via AI, login in to the local OCP console. The
following creates and associates the required objects for the new Node and
resolves the error from the initial creation.

#. Make note of the MAC address of the newly created Node

#. Go to :menuselection:`Compute --> MachineSets`

   - Edit the "worker" MachineSet
   - Increase the "Desired count" by +1

#. Go To :menuselection:`Compute --> Machines`

   - Copy & paste the Name of newly created machine to notepad

#. Go to :menuselection:`Compute --> Bare Metal Hosts`

   - Click :menuselection:`Add Host --> New from Dialog`
   - Add Name (ex. worker3)
   - Add Boot MAC Address (saved earlier when creating Node)
   - Disable "Enable power management"
   - Click Create

#. Modify newly created Bare Metal Hosts
   
   - Before editing new object, copy "spec" section from an older BMH object
   - Edit new BMH object
   - Click YAML tab
   - Replace "spec" section with older BMH "spec"
   - Be sure to use the new Node bootMACAddress and consumerRef/name
   - Click Save
   - Copy & paste uid to be used in next step

#. Go to :menuselection:`Compute --> Nodes`

   - Select/edit new Node
   - Click YAML tab
   - Add following annotation

     .. code-block:: yaml

        machine.openshift.io/machine: openshift-machine-api/<Name of new machine created in step2>

   - Replace "spec" section with following "spec"

     .. code-block:: yaml

        spec:
        providerID: >-
          baremetalhost:///openshift-machine-api/<name>/<uid>

   - Click Save

