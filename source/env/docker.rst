Docker Lab
==========

Some notes on installing Docker.

Install Docker
--------------

Simple install of docker-ce on Fedora/RHEL

#. Install docker-ce

   .. code-block:: bash

      sudo dnf install dnf-plugins-core
      sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
      sudo dnf install docker-ce docker-ce-cli containerd.io

      sudo systemctl enable --now docker

      # Add user to docker group
      usermod -a -G docker $USER
      newgrp docker

#. Test install... hello-world

   .. code-block:: bash

      docker run hello-world

Create Docker tarball
---------------------

Option to download docker-ce and dependencies in order to create a tarball for
installing on workstation in disconnected environment.

.. note:: These instructions assume you haven't isntalled docker-ce or any of the dependencies.

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

      cd ~/docker

      sudo tar -cvzf docker-deps-rpms.tar.gz *.rpm

#. Install docker

   .. code-block:: bash

      cd ~/docker

      sudo dnf localinstall *.rpm

      sudo systemctl enable --now docker

      # Add user to docker group
      sudo usermod -a -G docker $USER
      newgrp docker

#. Test install... hello-world

   .. code-block:: bash

      docker run hello-world

