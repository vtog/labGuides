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

#. Download RPM's.

   .. code-block:: bash

      sudo dnf install --downloadonly --downloaddir=$HOME/docker docker-ce docker-ce-cli containerd.io

#. Find docker dependencies.

   .. code-block:: bash

      cd ~/docker
      sudo dnf localinstall *.rpm

   .. important:: Do not install, select N to continue.

   .. note:: The command should produce a list like the following

      .. code-block:: bash

         Dependencies Resolved

         ===============================================================================================================================================================================================
          Package                                         Arch                         Version                                         Repository                                                  Size
         ===============================================================================================================================================================================================
         Installing:
          containerd.io                                   x86_64                       1.6.19-3.1.el7                                  /containerd.io-1.6.19-3.1.el7.x86_64                       114 M
          docker-ce                                       x86_64                       3:23.0.2-1.el7                                  /docker-ce-23.0.2-1.el7.x86_64                              94 M
          docker-ce-cli                                   x86_64                       1:23.0.2-1.el7                                  /docker-ce-cli-23.0.2-1.el7.x86_64                          34 M
         Installing for dependencies:
          audit-libs-python                               x86_64                       2.8.5-4.el7                                     rhel-7-server-rpms                                          77 k
          checkpolicy                                     x86_64                       2.5-8.el7                                       rhel-7-server-rpms                                         295 k
          container-selinux                               noarch                       2:2.119.2-1.911c772.el7_8                       rhel-7-server-extras-rpms                                   40 k
          docker-buildx-plugin                            x86_64                       0.10.4-1.el7                                    docker-ce-stable                                            12 M
          docker-ce-rootless-extras                       x86_64                       23.0.2-1.el7                                    docker-ce-stable                                           8.8 M
          docker-compose-plugin                           x86_64                       2.17.2-1.el7                                    docker-ce-stable                                            12 M
          docker-scan-plugin                              x86_64                       0.23.0-3.el7                                    docker-ce-stable                                           3.8 M
          fuse-overlayfs                                  x86_64                       0.7.2-6.el7_8                                   rhel-7-server-extras-rpms                                   55 k
          fuse3-libs                                      x86_64                       3.6.1-4.el7                                     rhel-7-server-extras-rpms                                   82 k
          libcgroup                                       x86_64                       0.41-21.el7                                     rhel-7-server-rpms                                          66 k
          libsemanage-python                              x86_64                       2.5-14.el7                                      rhel-7-server-rpms                                         113 k
          policycoreutils-python                          x86_64                       2.5-34.el7                                      rhel-7-server-rpms                                         457 k
          python-IPy                                      noarch                       0.75-6.el7                                      rhel-7-server-rpms                                          32 k
          setools-libs                                    x86_64                       3.3.8-4.el7                                     rhel-7-server-rpms                                         620 k
          slirp4netns                                     x86_64                       0.4.3-4.el7_8                                   rhel-7-server-extras-rpms                                   82 k

         Transaction Summary
         ===============================================================================================================================================================================================
         Install  3 Packages (+15 Dependent packages)

#. Downlad docker rpm dependencies.

   .. code-block:: bash

      sudo dnf install --downloadonly --downloaddir=/home/vince/docker \
        audit-libs-python \
        checkpolicy \
        container-selinux \
        docker-buildx-plugin \
        docker-ce-rootless-extras \
        docker-compose-plugin \
        docker-scan-plugin \
        fuse-overlayfs \
        fuse3-libs \
        libcgroup \
        libsemanage-python \
        policycoreutils-python \
        python-IPy \
        setools-libs \
        slirp4netns

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

