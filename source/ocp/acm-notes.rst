Advanced Cluster Management
===========================

This is a work in progress. Needed to capture the scripts used to import bare
metal hosts.

The following script creates the necessary objects for ACM Host Inventory list:

.. code-block:: bash
   :linenos:
   :emphasize-lines: 30,31,35,45,47,53,55,131,159,161,165

   #/bin/bash

   # Create output dir if not exists, delete old one if exists.

   if [[ -d output ]]; then
       rm -rf output
       mkdir -p output
   else
       mkdir -p output
   fi

   # Take "nodes" CSV and create bare-metal resources for cluster

   for host in `cat nodes|grep -v Hostname|awk -F "," '{print $1}'`; do
   HOST=`grep $host nodes|awk -F "," '{print $1}'`;
   BMCIP=`grep $host nodes|awk -F "," '{print $2}'`;
   HOSTIP=`grep $host nodes|awk -F "," '{print $3}'`;
   MAC1=`grep $host nodes|awk -F "," '{print $4}'`;
   MAC2=`grep $host nodes|awk -F "," '{print $5}'`;
   MAC3=`grep $host nodes|awk -F "," '{print $6}'`;
   MAC4=`grep $host nodes|awk -F "," '{print $7}'`;
   MAC5=`grep $host nodes|awk -F "," '{print $8}'`;
   MAC6=`grep $host nodes|awk -F "," '{print $9}'`;

   # NmState

   cat <<EOF > ./output/$HOST-secret.yaml
   apiVersion: v1
   data:
     password: <idrac_password>
     username: <idrac_username>
   kind: Secret
   metadata:
     name: bmc-$HOST
     namespace: <name>
   type: Opaque
   EOF

   cat <<EOF > ./output/$HOST-nmstate.yaml
   apiVersion: agent-install.openshift.io/v1beta1
   kind: NMStateConfig
   metadata:
     labels:
       agent-install.openshift.io/bmh: $HOST
       infraenvs.agent-install.openshift.io: <namespace_name>
     name: $HOST
     namespace: <name>
   spec:
     config:
       dns-resolver:
         config:
           search:
           - lab.local
           server:
           - 192.168.1.68
       interfaces:
       - name: eno12399np0
         type: ethernet
         state: up
         mtu: 9000
       - name: eno12409np1
         type: ethernet
         state: up
         mtu: 9000
       - name: ens1f0np0
         type: ethernet
         state: up
         mtu: 9000
       - name: ens1f1np1
         type: ethernet
         state: up
         mtu: 9000
       - name: ens3f0np0
         type: ethernet
         state: up
         mtu: 9000
       - name: ens3f1np1
         type: ethernet
         state: up
         mtu: 9000
       - name: bond0
         type: bond
         mtu: 9000
         state: up
         link-aggregation:
           mode: active-backup
           port:
           - eno12399np0
           - eno12409np1
         ipv4:
           address:
           - ip: $HOSTIP
             prefix-length: 24
           dhcp: false
           enabled: true
         ipv6:
           enabled: false
       - name: bond1
         type: bond
         mtu: 9000
         state: up
         link-aggregation:
           mode: active-backup
           port:
           - ens1f0np0
           - ens1f1np1
         ipv4:
           address:
           dhcp: false
           enabled: false
         ipv6:
           enabled: false
       - name: bond2
         type: bond
         mtu: 9000
         state: up
         link-aggregation:
           mode: active-backup
           port:
           - ens3f0np0
           - ens3f1np1
         ipv4:
           address:
           dhcp: false
           enabled: false
         ipv6:
           enabled: false
       routes:
         config:
         - destination: 0.0.0.0/0
           next-hop-address: 192.168.1.1
           next-hop-interface: bond0
           table-id: 254
     interfaces:
     - macAddress: $MAC1
       name: eno12399np0
     - macAddress: $MAC2
       name: eno12409np1
     - macAddress: $MAC3
       name: ens1f0np0
     - macAddress: $MAC4
       name: ens1f1np1
     - macAddress: $MAC5
       name: ens3f0np0
     - macAddress: $MAC6
       name: ens3f1np1
   EOF

   cat <<EOF > ./output/$HOST-baremetal.yaml
   apiVersion: metal3.io/v1alpha1
   kind: BareMetalHost
   metadata:
     annotations:
       bmac.agent-install.openshift.io/hostname: $HOST
       inspect.metal3.io: disabled
     finalizers:
     - baremetalhost.metal3.io
     labels:
       infraenvs.agent-install.openshift.io: <namespace_name>
     name: $HOST
     namespace: <name>
   spec:
     automatedCleaningMode: disabled
     bmc:
       address: idrac-virtualmedia://$BMCIP/redfish/v1/Systems/System.Embedded.1
       credentialsName: bmc-$HOST
       disableCertificateVerification: true
     bootMACAddress: $MAC1
     customDeploy:
       method: start_assisted_install
     online: true
   EOF

   done;

   echo "If storage nodes are included don't forget to manually update/fix nmstate object!!!"

The script uses the following flat variables file for PowerEdge R660 which
includes 3 NICs:

.. code-block:: bash

   Hostname,DRAC IP,IP,eno12399np0,eno12409np1,ens1f0np0,ens1f1np1,ens3f0np0,ens3f1np1
   control-00,192.168.1.65,192.168.1.136,A0:88:C2:33:D4:32,A0:88:C2:33:D4:33,a0:88:c2:6b:c6:e8,a0:88:c2:6b:c6:e9,a0:88:c2:6b:c8:7c,a0:88:c2:6b:c8:7d
   control-01,192.168.1.66,192.168.1.137,A0:88:C2:33:F9:52,A0:88:C2:33:F9:53,a0:88:c2:6b:ca:48,a0:88:c2:6b:ca:49,a0:88:c2:6b:ca:60,a0:88:c2:6b:ca:61
   control-02,192.168.1.99,192.168.1.138,A0:88:C2:33:B7:52,A0:88:C2:33:B7:53,a0:88:c2:ac:c4:04,a0:88:c2:ac:c4:05,a0:88:c2:ac:c8:ac,a0:88:c2:ac:c8:ad
   storage-00,192.168.1.89,192.168.1.139,A0:88:C2:33:F9:2E,A0:88:C2:33:F9:2F,a0:88:c2:6b:c5:f8,a0:88:c2:6b:c5:f9,,
   storage-01,192.168.1.90,192.168.1.140,A0:88:C2:33:FC:D0,A0:88:C2:33:FC:D1,a0:88:c2:6b:c6:40,a0:88:c2:6b:c6:41,,
   storage-02,192.168.1.91,192.168.1.141,A0:88:C2:33:9F:34,A0:88:C2:33:9F:35,a0:88:c2:6b:c7:88,a0:88:c2:6b:c7:89,,
   storage-03,192.168.1.92,192.168.1.142,A0:88:C2:33:F7:A8,A0:88:C2:33:F7:A9,a0:88:c2:6b:c4:b8,a0:88:c2:6b:c4:b9,,
   worker-00,192.168.1.68,192.168.1.143,A0:88:C2:33:F4:BA,A0:88:C2:33:F4:BB,a0:88:c2:6b:ca:6c,a0:88:c2:6b:ca:6d,a0:88:c2:6b:c3:e8,a0:88:c2:6b:c3:e9
   worker-01,192.168.1.69,192.168.1.144,A0:88:C2:34:05:A6,A0:88:C2:34:05:A7,a0:88:c2:6b:c8:98,a0:88:c2:6b:c8:99,a0:88:c2:6b:c6:d4,a0:88:c2:6b:c6:d5
   worker-02,192.168.1.70,192.168.1.145,A0:88:C2:33:F4:CC,A0:88:C2:33:F4:CD,a0:88:c2:6b:c6:38,a0:88:c2:6b:c6:39,a0:88:c2:6b:c5:7c,a0:88:c2:6b:c5:7d
   worker-03,192.168.1.71,192.168.1.146,A0:88:C2:33:D4:D4,A0:88:C2:33:D4:D5,a0:88:c2:6b:c7:f8,a0:88:c2:6b:c7:f9,a0:88:c2:6b:c8:48,a0:88:c2:6b:c8:49
   worker-04,192.168.1.72,192.168.1.147,A0:88:C2:33:A7:EC,A0:88:C2:33:A7:ED,a0:88:c2:6b:c6:90,a0:88:c2:6b:c6:91,a0:88:c2:6b:c6:1c,a0:88:c2:6b:c6:1d
