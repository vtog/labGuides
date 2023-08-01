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

Can't Remove Object
-------------------
   
I've noticed deleting PVC sometimes doesn't work and they'll be stuck in the
"Terminating" phase.  The following command will remove them:
 
.. code-block:: bash
 
   oc patch pvc <PVC_NAME> -p '{"metadata":{"finalizers":null}}'

Configure an htpasswd Identitiy Provider
----------------------------------------
 
After configuring local storage and a PVC for the local registry, you may
require an Identity Provider. These steps will get you started with htpasswd.
 
.. attention:: I've noticed without this, access to the local registry doesn't
   work.
 
#. Create your flat file with a user name and hashed password
 
   .. code-block:: bash
 
      htpasswd -c -B -b </path/to/users.htpasswd> <user_name> <password>
 
#. Add or delete users as needed
 
   - Add
 
     .. code-block:: bash
 
        htpasswd -B -b </path/to/users.htpasswd> <user_name> <password>
 
   - Delete
 
     .. code-block:: bash
 
        htpasswd -D users.htpasswd <username>
 
#. From the OCP console create the HTPasswd identity provider
 
   #. Go to :menuselection:`Administration --> Cluster Settings` and click the
      Configuration tab
   #. Filter the list for "oath". Click the "OAuth" resource
   #. In the "Identity providers" section click "Add" and select "HTPasswd"
   #. Give the new object a unique name
   #. Click "Browse" and upload the file created earlier
   #. Click "Add"
 
#. Update the htpasswd identity provider
 
   #. Get secret
 
      .. code-block:: bash
 
         oc get secret htpass-secret -ojsonpath={.data.htpasswd} -n openshift-config | base64 --decode > users.htpasswd
 
   #. Add or delete users (see step 2)
   #. Update secret
 
      .. code-block:: bash
 
         oc create secret generic htpass-secret --from-file=htpasswd=users.htpasswd --dry-run=client -o yaml -n openshift-confi
 
#. If you remove a user from htpasswd you must manually remove the user resources from OCP
 
   .. code-block:: bash
 
      oc delete user <username>
 
      #AND
 
      oc delete identity <identity_provider>:<username>

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

OCP Cert Expiry and Resolution
------------------------------
 
In the event that oauth is down, indicated by "connection refused" running any
OC command against the API. The issue is most likely caused by an expired
internal cluster certificate. Internal cluster certs have an expiry of 30d.
Under normal circumstances these certs are auto renewed. By running the
following commands you can confirm expired certs and resolve the issue.
 
#. SSH to any master node.
 
   .. code-block:: bash
 
      ssh core@master1
      sudo -s
 
#. Export recovery KUBECONFIG for local cluster management.
 
   .. code-block:: bash
 
      export KUBECONFIG=/etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/node-kubeconfigs/localhost-recovery.kubeconfig
 
#. View pending CSR's (should see several in the pending state).
 
   .. code-block:: bash
 
      oc get csr
 
#. Approve all CSR's.
 
   .. code-block:: yaml
 
      oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs --no-run-i
 
#. Repeat steps 3 and 4 until all pending CSR's are approved.
 
NOTES

#. Download for review csr-signer cert and key.
 
   .. code-block:: bash
 
      oc extract secret/csr-signer -n openshift-kube-controller-manager --to /home/user/ --confirm
 
#. View csr-signer cert (this shows the 30d expiry)
 
   .. code-block:: bash
 
      openssl x509 -text -noout -in /home/user/tls.crt

Starting the Cluster
--------------------
 
Bringing the cluster back up is much more simple than the shutdown procedure.
You just have to start nodes in the right order for the best results.
 
#. Start your master nodes *"master 1 - 3"*

   Once they have booted we can check that they are healthy using
   :code:`oc get nodes`

   .. note:: All nodes should be in a ready state before continuing on to your infra
      nodes.

#. Start your infra nodes *"worker 7 - 9"*

   Once your infra nodes have booted you can ensure the infra nodes are showing
   in a ready state :code:`oc get nodes`, and that
   :code:`oc get pods --all-namespaces` shows the logging, metrics, router and
   registry pods have started and are healthy.
 
#. Start your worker nodes *"worker 4 - 6"*

   Once your worker nodes have booted you can ensure that all nodes are showing
   in a ready state with :code:`oc get nodes`. Refer to the health check
   documentation for a more in-depth set of checks.

#. Start your applications

   Now that your cluster has started and is healthy, you can now start your
   application workload. If you chose to simply shutdown your worker nodes
   without draining workload then your applications will be restarting on the
   nodes they were previously located, otherwise you will need to increase the
   number of replica's or *'uncordon'* nodes depending on the approach you
   took.

#. Health Check

   Finally, check that your application pods have started correctly
   :code:`oc get pods --all-namespaces` and perform any checks that may be
   necessary on your application to prove that it is available and healthy.

