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

Managing CLI Profiles
---------------------

The ability to manage multiple clusters via the CLI is possible with "oc
config". Here's an example of my "~/.kube/config" file.

.. note:: All the required certs will be found in the kubeconfig file for each
   cluster.

#. Use the following template. Copy to "~/.kube/config" on your client.

   .. code-block:: yaml
      :emphasize-lines: 11-14, 28-31, 36, 48-51

      apiVersion: v1
      clusters:
      - cluster:
          certificate-authority-data: <add_clusterCert>
          server: https://api.ocp1.lab.local:6443
        name: ocp1
      - cluster:
          certificate-authority-data: <add_clusterCert>
          server: https://api.ocp2.lab.local:6443
        name: ocp2
      - cluster:
          certificate-authority-data: <add_clusterCert>
          server: https://api.ocp3.lab.local:6443
        name: ocp3
      - cluster:
          certificate-authority-data: <add_clusterCert>
          server: https://api.ocp4.lab.local:6443
        name: ocp4
      contexts:
      - context:
          cluster: ocp1
          user: admin/ocp1
        name: ocp1
      - context:
          cluster: ocp2
          user: admin/ocp2
        name: ocp2
      - context:
          cluster: ocp3
          user: admin/ocp3
        name: ocp3
      - context:
          cluster: ocp4
          user: admin/ocp4
        name: ocp4
      current-context: ocp3
      kind: Config
      preferences: {}
      users:
      - name: admin/ocp1
        user:
          client-certificate-data: <add_clientCert>
          client-key-data: <add_clientKey>
      - name: admin/ocp2
        user:
          client-certificate-data: <add_clientCert>
          client-key-data: <add_clientKey>
      - name: admin/ocp3
        user:
          client-certificate-data: <add_clientCert>
          client-key-data: <add_clientKey>
      - name: admin/ocp4
        user:
          client-certificate-data: <add_clientCert>
          client-key-data: <add_clientKey>

#. Now we can view the available clusters.

   .. code-block:: bash

      oc config get-contexts

   .. image:: ./images/config-get-context.png

#. Set the cluster context to the cluster you want to manage.

   .. code-block:: bash

      oc config use-context ocp4

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

#. If needed reboot node. Typically node will automatically reboot but if not
   run following command.

   .. code-block:: yaml

      ssh core@host11.lab.local sudo reboot

MCP and Performance Profile
---------------------------
In a cluster it's typical to see different machine types running. By default
the cluster has two machine config pools(MCP) , "master" and "worker". When
applying a performance profile, they are machine specific, and applied to the
nodes in an MCP. In order to support this a new MCP needs to be created for
each machine type.

.. tip:: Simultaneously upgrade multiple nodes. The default is one at a time.

   .. code-block:: bash

      oc patch mcp worker --type merge --patch '{"spec": {"maxUnavailable": 2}}'

#. Create new MCP yaml file

   .. important:: Be sure to include "worker" in the "matchExpressions" section.

   .. code-block:: yaml
      :emphasize-lines: 4, 7, 11, 14

      apiVersion: machineconfiguration.openshift.io/v1
      kind: MachineConfigPool
      metadata:
        name: small
        labels:
          machineconfiguration.openshift.io/role: small
          pools.operator.machineconfiguration.openshift.io/small: ""
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
          highPowerConsumption: false
          perPodPowerManagement: false
          realTime: false
        net:
          userLevelNetworking: true
          devices:
            - interfaceName: “enp1s0”
            - interfaceName: “ens2s0”

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

      cat << EOF > ./.toolboxrc
      REGISTRY=mirror.lab.local:8443
      IMAGE=rhel9/support-tools
      #IMAGE=centos/tools:latest
      EOF

Configure an htpasswd Identity Provider
---------------------------------------

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

#. If you remove a user from htpasswd you must manually remove the user
   resources from OCP

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
      sudo -i

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


KubeletConfig podPidsLimit
--------------------------
In some cases the deafult 4096 is not enough. Adding this example as the
solution doc example has mis-aligned yaml.

#. Use the following yaml to set the new "podPidsLimit"

   .. code-block:: yaml

      apiVersion: machineconfiguration.openshift.io/v1
      kind: KubeletConfig
      metadata:
        name: set-pid-limit-kubelet
      spec:
        machineConfigPoolSelector:
          matchLabels:
            pools.operator.machineconfiguration.openshift.io/worker: ''
        kubeletConfig:
          podPidsLimit: 8192

   .. note:: This will casue MCP to Update and reboot each node in the
      designated machine config pool.

#. Confirm new limit is in place.

   .. code-block:: bash

      ssh core@host33 cat /etc/kubernetes/kubelet.conf | grep -i podPidsLimit

Append or Delete kernel argument
--------------------------------

I have run into issues where an argument needs to be manually added back to
the node to satisfy MCP. The following walks through the process.

.. note:: This is taken directly from the following solution doc:

   `How to add or remove kernel argument from RHCOS node in RHOCP 4
   <https://access.redhat.com/solutions/6891971>`_

1. Cordon node

   .. code-block:: bash

      oc adm cordon <node1>

#. Drain node

   .. code-block:: bash

      oc adm drain <node1> --ignore-daemonsets --delete-emptydir-data

#. SSH to node


   .. code-block:: bash

      ssh core@<node1>

#. Check kernel arguments

   .. code-block:: bash

      sudo rpm-ostree kargs

#. Append or delete kernel arguments

   APPEND:

   .. code-block:: bash

      sudo rpm-ostree kargs --append='<key>=<value>'

   DELETE:

   .. code-block:: bash

      sudo rpm-ostree kargs --delete <key>=<value>

#. Confirm kernel argument changes

   .. code-block:: bash

      sudo rpm-ostree kargs

#. When satisfied uncordon node

   .. code-block:: bash

      oc adm uncordon <node1>

Change Cluster Network MTU
--------------------------

It's possible to change the interface MTU post deployment but I recommend
getting this right at install time. The following is based on:
`Changing the MTU for the cluster network
<https://docs.openshift.com/container-platform/4.12/networking/changing-cluster-network-mtu.html>`_

.. note:: In the OCP doc they use a machine config to change the nodes
   interface MTU. I found this did NOT work. I simply used nmcli to chagne the
   value.

.. important:: This is for **OVN-kubernetes** only.  For OpenShift SDN see
   official documentation.

.. attention:: Tested with 4.12

#. Confirm current MTU, see "Status" section.

   .. code-block:: bash

      oc describe network.config cluster

   .. code-block:: bash
      :caption: OUTPUT
      :emphasize-lines: 5,6

      Status:
        Cluster Network:
          Cidr:               10.128.0.0/14
          Host Prefix:        23
        Cluster Network MTU:  1400
        Network Type:         OVNKubernetes
        Service Network:
          172.30.0.0/16

#. Confirm **primary interace**, in my example it's "enp1so.122".

   .. note:: Check all interfaces. They should be the same but confirm.

   .. code-block:: bash

      ssh core@host51 nmcli -g connection.interface-name c show ovs-if-phys0

#. Update the network interface MTU. The type of interface will dictate where
   to make the change. In my example I use VLAN interfaces so will need to
   change the parent ethernet interface. It doesn't hurt to change both but
   vlan interfaces inherit this setting from the parent.

   .. attention:: Be sure to update all the "master" nodes.

   .. code-block:: bash

      ssh core@host51

      sudo nmcli con modify enp1s0 ethernet.mtu 9000
      sudo nmcli device reapply enp1s0

#. Start the MTU update

   .. note:: In my example we're going from 1400 to 8900. OVN requires 100
      bytes of padding. The interface will be set to 9000.

   .. attention:: This will cause each node to reboot via the machine config
      process. Be sure to let this process finish before proceeding.

   .. code-block:: bash

      oc patch Network.operator.openshift.io cluster --type=merge --patch \
      '{"spec": { "migration": { "mtu": { "network": { "from": 1400, "to": 8900 } , "machine": { "to" : 9000 } } } } }'

#. Verify MCP has completed its changes via "watch".

   .. code-block:: bash

      watch "oc get nodes; echo; oc get mcp"

#. Verify cluster MTU update.

   .. code-block:: bash

      oc describe network.config cluster

   .. code-block:: bash
      :caption: OUTPUT
      :emphasize-lines: 5,9,11,12

      Status:
        Cluster Network:
          Cidr:               10.128.0.0/14
          Host Prefix:        23
        Cluster Network MTU:  8900
        Migration:
          Mtu:
            Machine:
              To:  9000
            Network:
              From:    1400
              To:      8900
        Network Type:  OVNKubernetes
        Service Network:
          172.30.0.0/16

#. Verify interfaces have correct MTU.

   .. note:: Be sure to check all "master" nodes.

   .. code-block:: bash

      ssh core@host51 ip a | grep -e enp -e br-


#. Finalize the MTU migration. Be sure previous changes are complete.

   .. attention:: This will cause each node to reboot via the machine config
      process. Be sure to let this process finish.

   .. code-block:: bash

      oc patch Network.operator.openshift.io cluster --type=merge --patch \
      '{"spec": { "migration": null, "defaultNetwork":{ "ovnKubernetesConfig": { "mtu": 8900 }}}}'

#. Verify MCP has completed its changes via "watch".

   .. code-block:: bash

      watch "oc get nodes; echo; oc get mcp"

#. Verify cluster MTU.

   .. code-block:: bash

      oc describe network.config cluster

   .. code-block:: bash
      :caption: OUTPUT
      :emphasize-lines: 5

      Status:
        Cluster Network:
          Cidr:               10.128.0.0/14
          Host Prefix:        23
        Cluster Network MTU:  8900
        Network Type:         OVNKubernetes
        Service Network:
          172.30.0.0/16
