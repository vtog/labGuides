Docker Lab
==========

Some notes on installing Docker.

Install Docker
--------------

#. Install docker-ce

   .. code-block:: bash

      sudo dnf install dnf-plugins-core
      sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
      sudo dnf install docker-ce docker-ce-cli containerd.io

      sudo systemctl enable --now docker
      
      # Add user to docker group
      usermod -a -G docker <user>
      newgrp docker

#. Test install... hello-world

   .. code-block:: bash

      docker run hello-world

Create Docker tarball
---------------------

.. note:: These instructions assume you haven't isntalled docker-ce.

#. Add docker-ce repo

   .. important:: Do not "install" docker-ce.

   .. code-block:: bash

      sudo dnf install dnf-plugins-core
      sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo

#. Download docker and dependencies RPM's

   .. code-block:: bash

      sudo dnf install --downloadonly --downloaddir=$HOME/docker docker-ce docker-ce-cli containerd.io

#. Create tarball

   .. code-block:: bash

      sudo tar -cvzf docker-deps-rpms.tar.gz *.rpm

#. Install docker

   .. code-block:: bash

      sudo dnf localinstall *.rpm

      sudo systemctl enable --now docker

      # Add user to docker group
      usermod -a -G docker <user>
      newgrp docker

#. Test install... hello-world

   .. code-block:: bash

      docker run hello-world

