MicroShift
==========

Quick list of steps to deploy MicroShift on RHEL 9.

Install
-------

#. Add the necessary repo's

   .. note:: My example shows OCP v4.19 on RHEL v9.6.

   .. code-block:: bash

      sudo subscription-manager repos \
        --enable rhocp-4.19-for-rhel-9-x86_64-rpms \
        --enable fast-datapath-for-rhel-9-x86_64-rpms

#. Install MicroShift and OpenShift client tools.

   .. code-block:: bash

      sudo dnf install microshift openshift-clients

#. Update firewall for default networks and ports

   .. code-block:: bash

      sudo firewall-cmd --add-source=10.42.0.0/16 --permanent
      sudo firewall-cmd --add-source=169.254.169.1 --permanent
      sudo firewall-cmd --add-port=6443/tcp --permanent
      sudo firewall-cmd --add-port=443/tcp --permanent
      sudo firewall-cmd --add-port=80/tcp --permanent
      sudo firewall-cmd --add-service=cockpit --permanent
      sudo firewall-cmd --reload
      sudo firewall-cmd --list-all

#. Copy pull-secret

   .. tip:: You can find your
      `pull secret here <https://console.redhat.com/openshift/install/pull-secret>`_

   .. code-block:: bash

      sudo cp $HOME/openshift-pull-secret /etc/crio/openshift-pull-secret
      sudo chown root:root /etc/crio/openshift-pull-secret
      sudo chmod 600 /etc/crio/openshift-pull-secret

#. Start MicroShift

   .. code-block:: bash

      sudo systemctl enable --now microshift

#. Copy kubeconfig for cli mgmt

   .. code-block:: bash

      mkdir -p ~/.kube
      sudo cp /var/lib/microshift/resources/kubeadmin/kubeconfig ~/.kube/config
      chown vince: ~/.kube/config

#. Check cluster-info

   .. code-block:: bash

      oc cluster-info

      oc get nodes

      oc get po -A

Uninstall
---------

#. Cleanup ALL data

   .. code-block:: bash

      sudo microshift-cleanup-data --all

#. Remove MicroShift

   .. code-block:: bash

      sudo dnf remove microshift -y
