OpenShift Day 2
===============

Privileged Deployment (root)
----------------------------

By default all deployed application pods run as nonroot. For **LAB/PoC
testing** the following procedure allows root privileges on a per project and
deployment basis.

.. attention:: For security reasons it's recommended to run as nonroot
   (default).

#. Update the "privileged" Security Context Constraints by adding the projects
   "default" service account.

   .. code-block:: bash

      oc edit scc privileged

   .. note:: You can apply this to any project and any service account in use
      with the deployment. In the following example we're using the "default"
      project and the "default" service account.

   .. code-block:: yaml
      :emphasize-lines: 4

      users:
      - system:admin
      - system:serviceaccount:openshift-infra:build-controller
      - system:serviceaccount:default:default

#. Update deployment. The following deployment highlights the required changes.

   .. code-block:: yaml
      :emphasize-lines: 5, 16, 24-28

      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: f5-hello-world-web
        namespace: default
      spec:
        replicas: 2
        selector:
          matchLabels:
            app: f5-hello-world-web
        template:
          metadata:
            labels:
              app: f5-hello-world-web
          spec:
            serviceAccountName: default
            containers:
            - env:
              - name: service_name
                value: f5-hello-world-web
              image: mirror.lab.local:8443/f5devcentral/f5-hello-world:latest
              imagePullPolicy: IfNotPresent
              name: f5-hello-world-web
              securityContext:
                runAsUser: 0
                privileged: true
                allowPrivilegeEscalation: true
                runAsNonRoot: false
                seccompProfile:
                  type: RuntimeDefault
                capabilities:
                  drop: ["ALL"]
              ports:
              - containerPort: 8080
                protocol: TCP

Schedule Control Nodes
----------------------

#. Enable

   .. code-block:: bash

      oc patch schedulers.config.openshift.io/cluster --type merge -p '{"spec":{"mastersSchedulable":true}}'

#. Disable

   .. code-block:: bash

      oc patch schedulers.config.openshift.io/cluster --type merge -p '{"spec":{"mastersSchedulable":false}}'

Pause MCP
---------

When making several changes via MCP it's beneficial to "pause" MCP from
restarting the nodes with each change. This way all changes are applied with a
single reboot. Set "paused" to "true", when finished set back to "false".

.. code-block:: bash

   oc patch mcp master --type=merge -p '{"spec": {"paused": true}}'

Force MCP to Update
-------------------

If MCP gets stuck try forcing the update to unstuck it.

#. Create file called "machine-config-daemon-force" in "/run"

   .. code-block:: bash

      ssh core@host11.lab.local sudo touch /run/machine-config-daemon-force

#. Edit node annotations

   .. code-block:: bash

      oc edit node host11

   Should look something like the following. Make change and ":wq".

   .. code-block:: yaml

      machineconfiguration.openshift.io/currentConfig: rendered-master-ed7befb1b258658c68e892964bbcf9e1
      machineconfiguration.openshift.io/desiredConfig: rendered-master-ed7befb1b258658c68e892964bbcf9e1
      machineconfiguration.openshift.io/reason: ""
      machineconfiguration.openshift.io/state: Done

#. Reboot node

   .. code-block:: yaml

      ssh core@host11.lab.local sudo reboot

MCP and Performance Profile
---------------------------
In a cluster it's typical to see different machine types running. By default
the cluster has two machine config pools(MCP) , "master" and "worker". When
applying a performance profile, they are machine specific, and applied to the
nodes in an MCP. In order to support this a new MCP needs to be created for
each machine type.

#. Create new MCP yaml file

   .. important:: Be sure to include "worker" in the "matchExpressions" section.

   .. code-block:: yaml
      :emphasize-lines: 4, 6, 10, 13

      apiVersion: machineconfiguration.openshift.io/v1
      kind: MachineConfigPool
      metadata:
        name: small
        labels:
          machineconfiguration.openshift.io/role: small
      spec:
        machineConfigSelector:
          matchExpressions:
            - {key: machineconfiguration.openshift.io/role, operator: In, values: [worker,small]}
        nodeSelector:
          matchLabels:
            node-role.kubernetes.io/small: ""
        pause: false

#. Create new MCP

   .. code-block:: bash

      oc create -f mcp-small.yaml

#. Verify new MCP

   .. attention:: The new pool will be there with no members (MACHINECOUNT = 0)

   .. code-block:: bash

      oc get mcp

#. Add node to MCP by adding label, in my case "small" as defined in step 1

   .. code-block:: bash

      oc label node host24 node-role.kubernetes.io/small=

#. Verify MCP now includes the node with the proper label

   .. code-block:: bash

      oc get mcp

#. Reference MCP in Performance Profile

   .. code-block:: yaml
      :emphasize-lines: 10, 12

      apiVersion: performance.openshift.io/v2
      kind: PerformanceProfile
      metadata:
        name: performance-small
      spec:
        cpu:
          isolated: 1-7
          reserved: 0-0
        machineConfigPoolSelector:
          pools.operator.machineconfiguration.openshift.io/small: ""
        nodeSelector:
          node-role.kubernetes.io/small: ""
        numa:
          topologyPolicy: single-numa-node
        hugepages:
          defaultHugepagesSize: "2M"
          pages:
            - count: 1024
              node: 0
              size: 2M
        additionalKernelArgs:
          - "default_hugepagesz=2M"
          - "hugepagesz=2M"
          - "hugepages=1024"
        realTimeKernel:
          enabled: false
        workloadHints:
          highPowerConsumption: true
          perPodPowerManagement: false
          realTime: false

#. Check allocated huge pages and kernel args

   .. code-block:: bash

      ssh core@host44 grep -i hugepages /proc/meminfo

      # and/or

      ssh core@host44 cat /boot/loader/entries/ostree-1-rhcos.conf

Stuck Terminating
-----------------

Sometimes when deleting a PVC it can get stuck in the "Terminating" phase. The
following command will remove it:
                                    
.. code-block:: bash          
                                    
   oc patch pvc <PVC_NAME> -p '{"metadata":{"finalizers":null}}'

.. note:: This could be true of any object, so check the metadata for
   finalizers.

Start toolbox (node)
--------------------
 
There's a script to start "toolbox" on each node. Toolbox is a container which
has several network tools to help troubleshoot the cluster/node.
 
#. To start, SSH to node and run the following cmd:
 
   .. code-block:: bash
 
      toolbox
 
#. To start an alternative toolbox image, create file "~/.toolboxrc" on the
   target node with the following content. In this example I'm using my local
   registry.
 
   .. code-block:: bash
 
      REGISTRY=mirror.lab.local:8443
      IMAGE=rhel9/support-tools
      #IMAGE=centos/tools:latest

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

      oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs --no-run-if-empty oc adm certificate approve

   .. important:: **Repeat this step until all pending CSR's are approved!**

#. To view the certs expiry date, extract the secret/csr-signer cert and key.

   .. code-block:: bash

      oc extract secret/csr-signer -n openshift-kube-controller-manager --to ./ --confirm

      openssl x509 -text -noout -in ./tls.crt

   .. image:: ./images/certexpiry.png

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

