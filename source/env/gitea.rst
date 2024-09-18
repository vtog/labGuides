Gitea
=====

Free self-hosted git service. My lab needs this for disconnected gitops
testing.

The following are the steps I took to deploy in my lab. For a full explanation
see `Gitea Installation <https://docs.gitea.com/category/installation>`_

Database Prep (MariaDB)
-----------------------

#. Install MariaDB (RHEL9).

   .. code-block:: bash

      sudo dnf install mariadb-server

#. Enable and start MariaDB.

   .. code-block:: bash

      sudo systemctl enable --now mariadb.service

   .. note:: Service listens on TCP port 3306

#. Login to database console as root

   .. code-block:: bash

      sudo mysql -u root -p

   .. note:: There should not be a passwd.

#. Create DB user for gitea

   .. code-block:: bash

      SET old_passwords=0;
      CREATE USER 'gitea'@'%' IDENTIFIED BY 'gitea';

#. Create DB

   .. code-block:: bash

      CREATE DATABASE giteadb CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_bin';

#. Grant DB privileges

   .. code-block:: bash

      GRANT ALL PRIVILEGES ON giteadb.* TO 'gitea';
      FLUSH PRIVILEGES;

#. Exit DB console and test connection

   .. code-block:: bash

      exit

      mysql --user=gitea --password=gitea giteadb

Install from binary
-------------------

Find the download version/platform/binary at
`Gitea Downloads <https://dl.gitea.com/gitea/>`_

.. important:: "su - root" to run the following commands.

#. Download with wget

   .. code-block:: bash

      wget https://dl.gitea.com/gitea/1.22.2/gitea-1.22.2-linux-amd64 -O gitea
      chmod +x gitea

#. Copy to /usr/local/bin

   .. code-block:: bash

      cp gitea /usr/local/bin/

   .. tip:: For the proper selinux policy use cp, don't mv.

#. Create git user.

   .. code-block:: bash

      groupadd --system git
      adduser \
         --system \
         --shell /bin/bash \
         --comment 'Git Version Control' \
         --gid git \
         --home-dir /home/git \
         --create-home \
         git

#. Create required directory structure.

   .. code-block:: bash

      mkdir -p /var/lib/gitea/{custom,data,log}
      chown -R git:git /var/lib/gitea/
      chmod -R 750 /var/lib/gitea/
      mkdir /etc/gitea
      chown root:git /etc/gitea
      chmod 770 /etc/gitea

Run Gitea as service
--------------------

#. Copy the sample gitea.service

   .. code-block:: bash

      wget https://raw.githubusercontent.com/go-gitea/gitea/release/v1.22/contrib/systemd/gitea.service -O gitea.service

#. Uncomment "mariadb.service" in gitea.service, cp to /etc/systemd/system/.

   .. code-block:: bash

      sudo cp gitea.service /etc/systemd/system

#. Enable, start and check status gitea

   .. code-block:: bash

      sudo systemctl enable --now gitea.service

      sudo systemctl status gitea

#. Allow gitea default mgmt port (3000).

   .. code-block:: bash

      firewall-cmd --add-port=3000/tcp --permanent
      firewall-cmd --reload

#. Browse to http://<server_IP>:3000/ and configure gitea. Should only need
   to add DB settings.

   .. image:: ./images/gitea-conf.png

#. Register Account / User

   .. image:: ./images/gitea-user.png
