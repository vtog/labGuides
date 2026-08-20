Customer Edge
=============

This lab will walk you through the process of deploying a customer edge (CE) on
KVM.

.. note:: This is not a complete guide to creating CE's.  It focus's on one use
   case. KVM-LAB.

#. From the XC console click on the ``Multi-Cloud Network Connect`` tile.

   .. image:: ./images/multi-cloud-network-connect.png

#. Under Manage select :menuselection:`Site Management --> Secure Mesh Sites v2`
   then click ``Add Secure Mesh Site``

   .. image:: ./images/add-secure-mesh.png

#. Fill out the site fields.

   A. Metadata

      1. Name: ``vtog-lab-local``

   #. Provider

      1. Provider Name: ``KVM``

      #. High Availability: ``Disable``

         .. note:: This option sets the cluster to single node or three nodes.

   #. Regional Edge

      1. Regional Edge Selection: ``Based on Geo-proximity``

         .. note:: By selecting "Specify Geography", you can select which two
            REs will be in use. A site will always be connected to two REs.

      #. Tunnel Type: ``IPSEC and SSL``

   #. Site Management

      1. Admin User Credentials: ``Add Public SSH key``

      #. Admin User Credentials: ``Configure Admin Password``

      #. DNS Servers: ``192.168.1.68``

      #. NTP Servers: ``192.168.1.68``

   #. When ready click ``Add Secure Mesh Site``

#. To bring up your site download the Image and Token

   A. Filter list by new site name: ``vtog-lab-local``

   #. Under Actions click the three dots of your site and click
      ``Download Image``, Save qcow2 file to your working directory.

   #. Under Actions click the three dots of your site and click
      ``Generate Node Token``, Copy cloud-init to working directory
      ``<site-name>-token``.

   #. Create the cloud-init ISO

      1. Create "meta-data"

         .. code-block:: bash

            cat <<EOF > ./meta-data
            {
            "instance-id": "iid-local01"
            }
            EOF

      #. Create "user-data"

         .. code-block:: bash

            cat <site-name>-token > user-data

      #. Create the ISO

         .. code-block:: bash

            mkisofs -output <site-name>-token.iso -volid cidata -joliet -rock -quiet -input-charset utf-8 "./user-data" "./meta-data" 

#. Create a new VM.

   .. note:: I'm using virt-manager to build the new VM.

   A. Click New

   #. Choose "Import existing disk image" and select the qcow2 file
      previously downloaded.
  
   #. For operationg system select "Red Hat Enterprise Linux 9.2"
  
   #. Set ``32768`` GB of memory and ``16`` CPUs

   #. Name the VM and bu sure to select "Customize configuration before
      install"

      .. warning:: If you miss this step you'll have to create a new VM. The
         token ISO must be present for the VM to initialize.

   #. Add CDROM:
      
      1. :menuselection:`Add Hardware --> Storage`

      #. Click the "Select or create custome storage" radial button

      #. Click "Manage" and select the token ISO created earlier

      #. Change Device type to "CDROM device"

      #. Click "Finish"

   #. Bigin Installation

.. important:: If all goes well you should see the new VM connect to the XC
   console and start the installing. "Site Admin State" should change to
   "Provisioning".
