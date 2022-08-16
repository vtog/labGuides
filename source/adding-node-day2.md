# Adding Node to Cluster

The Assisted Installer has the ability to add Nodes to the cluster but the new
Node is not created in the same way as the original Nodes. The original Nodes
are part of a MachineSet and associated with bare metal host objects. The new
Node shows up as available but the Node Overview via the console shows errors.
After adding the new Node via AI, login in to the local OCP console. The
following creates and associates the required objects for the new Node and
resolves the error from the initial creation.

1. Make note of the MAC address of the newly created Node

2. Go to Compute --> MachineSets

   - Edit the "worker" MachineSet
   - Increase the "Desired count" by +1

3. Go To Compute --> Machines

   - Copy & paste the Name of newly created machine to notepad

4. Go to Compute --> Bare Metal Hosts

   - Click Add Host --> New from Dialog
   - Add Name (ex. worker3)
   - Add Boot MAC Address (saved earlier when creating Node)
   - Disable "Enable power management"
   - Click Create

5. Modify newly created Bare Metal Hosts
   
   - Before editing new object, copy "spec" section from an older BMH object
   - Edit new BMH object
   - Click YAML tab
   - Replace "spec" section with older BMH "spec"
   - Be sure to use the new Node bootMACAddress and consumerRef/name
   - Click Save
   - Copy & paste uid to be used in next step

6. Go to Compute --> Nodes
   
   - Select/edit new Node
   - Click YAML tab
   - Add following annotation
     ```yaml
     machine.openshift.io/machine: openshift-machine-api/<Name of new machine created in step2>
     ```
   - Replace "spec" section with following "spec"
     ```yaml
     spec:
     providerID: >-
       baremetalhost:///openshift-machine-api/<name>/<uid>
     ```
   - Click Save
