Setup Fedora/RHEL
=================

These instruction configure RHEL9 or Fedora with my preferred settings.

#. If needed setup fusion free and non-free

   .. attention:: Optional, these repo's may not be needed.

   .. code-block:: bash

      #Fedora
      sudo dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm 
      sudo dnf install https://mirrors.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

      #RHEL
      sudo dnf install --nogpgcheck https://dl.fedoraproject.org/pub/epel/epel-release-latest-$(rpm -E %rhel).noarch.rpm
      sudo dnf install --nogpgcheck https://mirrors.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm 
      sudo dnf install --nogpgcheck https://mirrors.rpmfusion.org/nonfree/el/rpmfusion-nonfree-release-$(rpm -E %rhel).noarch.rpm

      sudo dnf install obs-studio

#. Install base packages

   .. code-block:: bash

      sudo dnf install zsh neovim neofetch terminator ksnip slack firewall-config zoom

#. Install dev packages

   .. code-block:: bash

      sudo dnf group install "Development Tools"
      sudo dnf install cmake httpd-tools python3-pip

#. Install virtualization

   .. code-block:: bash

      sudo dnf group install --with-optional "virtualization"

      sudo systemctl enable --now libvirtd

   .. attention:: You'll need to configure firewalld to allow external traffic
      to connect to the virtual network via the host. The following
      firewall-cmd's allow the virtual network to access port 53 and any
      external host access to the virtual network.

      .. code-block:: bash

         sudo firewall-cmd --add-source=192.168.122.0/24 --zone=home --permanent
         sudo firewall-cmd --add-service=dns --zone=home --permanent

#. Insall packages via Sofware store.

   - Brave
   - Yubico Authenticator
   - Visual Studio Code

#. Update PIP and install misc packages

   .. code-block:: bash
      
      pip install pip -U
      
      # add misc packages
      pip install ansible awscli pygments wheel

#. Add Sphinx build environment

   .. code-block:: bash
   
      pip install sphinx==5.3.0 docutils==0.16 sphinx_rtd_theme sphinx-copybutton

      # F5 Theme
      pip install f5_sphinx_theme recommonmark sphinxcontrib.addmetahtml sphinxcontrib.nwdiag sphinxcontrib.blockdiag sphinxcontrib-websupport
      sudo dnf install graphviz

#. Modify sshd

   .. attention:: This assumes you've set up pki.

   .. code-block:: bash
   
      # modify following settings     
      vim /etc/ssh/sshd_config
         PermitRootLogin no
         PasswordAuthentication no
               
      # reload service
      systemctl restart sshd

#. Add user to wheel group **(If Needed)**

   .. code-block:: bash
   
      usermod -a -G wheel <user>

#. Modify sudo with NOPASSWD option

   .. code-block:: bash

      # Modify sudo with "visudo" and uncomment or modify the follow line
      %wheel  ALL=(ALL)       ALL
      # to
      %wheel  ALL=(ALL)       NOPASSWD: ALL

#. Modify LDAP shell attribute to change default shell **(IF Needed. Corp
   laptop required this.)**

   .. code-block:: bash

      getent passwd <user-name>
      sudo sss_override user-add <user-name> -s <new-shell>
      sudo systemctl restart sssd
      getent passwd <user-name>
      sudo sss_override user-show <user-name>

#. Setup .dotfiles

   .. note:: This assumes my "dotfiles" github repo exists.

   .. code-block:: bash

      git clone -b rhel --separate-git-dir=$HOME/.dotfiles git@github.com:vtog/.dotfiles.git tmpdotfiles
      rsync --recursive --verbose --exclude '.git' tmpdotfiles/ $HOME/
      rm -rf ~/tmpdotfiles
      dots config --local status.showUntrackedFiles no

#. Setup Spaceship-prompt

   .. code-block:: bash

      git clone https://github.com/spaceship-prompt/spaceship-prompt.git --depth=1 ~/git/spaceship-prompt
      sudo ln -sf ~/git/spaceship-prompt/spaceship.zsh /usr/share/zsh/site-functions/prompt_spaceship_setup      
      source ~/.zshrc

#. Install vim-plug (neovim)

   .. code-block:: bash

      curl -fLo ~/.local/share/nvim/site/autoload/plug.vim --create-dirs \
          https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

      # Update vim!
      vim
      : PlugInstall
      : q
      : q

#. Install NeoVIM from Source **(If Needed)**

   .. code-block:: bash

      sudo dnf install libtool autoconf automake cmake gcc gcc-c++ make pkgconfig unzip patch gettext curl
      git clone git@github.com:neovim/neovim.git ~/git/neovim
      cd ~/git/neovim
      make distclean
      make CMAKE_BUILD_TYPE=Release
      sudo make install

#. Insall Terminator from Source **(If Needed)**

   .. code-block:: bash

      sudo dnf install python3-gobject python3-configobj python3-psutil vte291 keybinder3 intltool gettext

      git clone git@github.com:gnome-terminator/terminator.git ~/git/terminator
      cd ~/git/terminator
      python3 setup.py build
      sudo python3 setup.py install --single-version-externally-managed --record=install-files.txt    

#. Install Alacritty from Source **(If Needed)**

   .. code-block:: bash

      git clone git@github.com:alacritty/alacritty.git ~/git/alacritty
      cd ~/git/alacritty
      cargo build --release
      sudo cp target/release/alacritty /usr/local/bin # or anywhere else in $PATH
      sudo tic -xe alacritty,alacritty-direct extra/alacritty.info

      # Create Desktop Entry
      sudo cp extra/logo/alacritty-term.svg /usr/share/pixmaps/Alacritty.svg
      sudo desktop-file-install extra/linux/Alacritty.desktop
      sudo update-desktop-databas

      # Create Man Page
      sudo mkdir -p /usr/local/share/man/man1
      gzip -c extra/alacritty.man | sudo tee /usr/local/share/man/man1/alacritty.1.gz > /dev/null
      gzip -c extra/alacritty-msg.man | sudo tee /usr/local/share/man/man1/alacritty-msg.1.gz > /dev/null

      # Create Zsh Shell Completion
      sudo cp extra/completions/_alacritty /usr/share/zsh/site-functions

#. Install docker-ce **(Not needed... Use Podman)**

   .. code-block:: bash

      sudo dnf install dnf-plugins-core
      sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
      sudo dnf install docker-ce docker-ce-cli containerd.io
      sudo systemctl start docker
      sudo systemctl enable docker
      
      # Add user to docker group
      usermod -a -G docker <user>
      newgrp docker

#. Install brave **(If Needed)**

   .. code-block:: bash

      sudo dnf install dnf-plugins-core
      sudo dnf config-manager --add-repo https://brave-browser-rpm-release.s3.brave.com/x86_64/
      sudo rpm --import https://brave-browser-rpm-release.s3.brave.com/brave-core.asc
      sudo dnf install brave-browser

