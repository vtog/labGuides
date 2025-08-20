NFS Server & Client
===================

Steps to create an NFS Server and mount the remote directory. My lab server IP
is "192.168.1.72".

Server
------

#. Install the nfs utilities.

   .. code-block:: bash

      sudo dnf install nfs-utils -y

#. Start the nfs-server daemon.

   .. code-block:: bash

      sudo systemctl enable --now nfs-server

#. Verify the listener.

   .. code-block:: bash

      rpcinfo -p | grep nfs

#. Create the directory, set the owner, and permissions.

   .. code-block:: bash

      sudo mkdir -p /mirror/nfs
      sudo chown -R nobody: /mirror/nfs
      sudo chmod -R 777 /mirror/nfs

#. Restart the nfs utilities.

   .. code-block:: bash

      sudo systemctl restart nfs-utils

#. Update "/etc/exports".

   .. note:: Set the subnet to match your requirements. In this example I'm
      allowing all clients on subnet "192.168.1.0/24" access to the mount.

   .. code-block:: bash

      echo "/mirrro/nfs 192.168.1.0/24(rw,sync,no_all_squash,root_squash)" | sudo tee -a /etc/exports

#. Export and check mount.

   .. code-block:: bash

      sudo exportfs -arv
      sudo exportfs -s

#. Update firewall to allow nfs.

   .. code-block:: bash

      sudo firewall-cmd --add-service=nfs --permanent
      sudo firewall-cmd --reload
      sudo firewall-cmd --list-all

   .. note:: For older nfs clients you may need to open the following ports

      .. code-block:: bash

         sudo firewall-cmd --add-service={nfs3,mountd,rpc-bind} --permanent
         sudo firewall-cmd --reload

Client
------

#. Install the nfs utilities.

   .. code-block:: bash

      sudo dnf insatll nfs-utils -y

#. Create the mount directory.

   .. code-block:: bash

      sudo mkdir -p /mnt/nfs

#. Mount the remote nfs directory.

   .. code-block:: bash

      sudo mount -t nfs 192.168.1.72:/mirror/nfs /mnt/nfs

#. Verify nfs mount.

   .. code-block:: bash

      mount | grep -i nfs
