Image Registry Quick Start
==========================

After configuring storage you can create a PVC for the local registry. This
quick start will cover the following topics:

- Configure the local Image Registry storage claim
- Local registry default route
- Create an HTPasswd file using linux

.. important:: These instructions assume you've configured a persistant volume
   (PV). More specifically followed the `Local Storage & ODF Operator Quick Start <./lso-odf-quick-start.html>`_

   For LSO only see `Local Storage Operator + Image Registry Quick Start <./lso-lr-quick-start.html>`_

Configure the Image Registry storage claim
-------------------------------------------

#. Change project

   .. code-block:: bash

      oc project openshift-image-registry

#. Set image registry to Managed by patching the config

   .. code-block:: bash

      oc patch configs.imageregistry.operator.openshift.io cluster --type merge --patch '{"spec":{"managementState":"Managed"}}'

#. Add the PVC by editing the image registry config

   .. code-block:: bash

      oc edit configs.imageregistry.operator.openshift.io cluster

      # Replace the "storage: {}" line with the following
      #
      # storage:
      #   pvc:
      #     claim:

#. Check pvc STATUS = "Bound"

   .. code-block:: bash

      oc get pvc

Set the Image Registry's default route
--------------------------------------

#. Set the defaultRoute to true

   .. code-block:: bash

      oc patch configs.imageregistry.operator.openshift.io/cluster --patch '{"spec":{"defaultRoute":true}}' --type=merge

#. Get the default registry route

   .. code-block:: bash

      HOST=$(oc get route default-route -n openshift-image-registry --template='{{ .spec.host }}')

#. Get the cluster’s default certificate and add to the clients local ca-trust
                                                                                                                               
   .. code-block:: bash                                                                                                     
                                                                                                                               
      oc get secret -n openshift-ingress router-certs-default -o go-template='{{index .data "tls.crt"}}' | base64 -d | sudo tee /etc/pki/ca-trust/source/anchors/${HOST}.crt  > /dev/null
                                                                                                                               
#. Update the clients local ca-trust                                                                                           
                                                                                                                               
   .. code-block:: bash                                                                                                     
                                                                                                                               
      sudo update-ca-trust enable                                                                                              
                                      
#. Log in with podman using the default route

   .. code-block:: bash

      podman login -u kubeadmin -p $(oc whoami -t) $HOST

Create an HTPasswd file using linux
-----------------------------------

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

