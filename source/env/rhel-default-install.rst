Setup Fedora/RHEL
=================

These instruction configure RHEL9 or Fedora with my preferred settings.

#. My default install of RHEL9 had ipv6 disabled. Here's how to enable it.

   .. code-block:: bash

      sudo sysctl -w net.ipv6.conf.all.disable_ipv6=0
      sudo sysctl -w net.ipv6.conf.default.disable_ipv6=0

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

      sudo dnf install obs-studio v4l2loopback

#. Install base packages

   .. code-block:: bash

      sudo dnf install zsh git rsync NetworkManager-tui firewall-config \
      cockpit cockpit-machines cockpit-composer util-linux-user \
      cronie cronie-anacron

#. Enable/start and open firewall for "cockpit" service

   .. tip:: To see the ports for any firewall service, "cat" the
      <service_name>.xml

      .. code-block:: bash

         cat /usr/lib/firewalld/services/vnc-server.xml

   .. code-block:: bash

      sudo systemctl enable --now cockpit.socket

   .. code-block:: bash

      sudo firewall-cmd --add-service=cockpit --permanent
      sudo firewall-cmd --reload
      sudo firewall-cmd --get-default-zone
      sudo firewall-cmd --list-all

#. Install dev packages

   .. code-block:: bash

      sudo dnf group install "Development Tools"

#. Install virtualization

   .. code-block:: bash

      #Fedora
      sudo dnf group install --with-optional "virtualization"

      #RHEL
      sudo dnf install virt-install virt-viewer virt-manager virt-top libguestfs-tools libvirt qemu-kvm

      sudo systemctl enable --now libvirtd

   .. tip:: Verify the system is ready to be a virtualization host:

      .. code-block:: bash

         sudo virt-host-validate

   .. attention:: Depending on your network configuration you may need to
      configure firewalld to allow external traffic to connect to the virtual
      network via the host. The following firewall-cmd's allow the virtual
      network to access port 53 and any external host access to the virtual
      network. I made the necessary changes to my network router and no longer
      need these changes.

      .. code-block:: bash

         sudo firewall-cmd --add-source=192.168.122.0/24 --zone=home --permanent
         sudo firewall-cmd --add-service=dns --zone=home --permanent
         sudo firewall-cmd --reload

#. Enable IOMMU

   .. code-block:: bash

      sudo grubby --update-kernel=ALL --args="intel_iommu=on iommu=pt"

   .. code-block:: bash

      sudo dmesg | grep "iommu: Default"

   .. tip:: How to remove argument

      .. code-block:: bash

         sudo grubby --update-kernel ALL --remove-args="intel_iommu=on iommu=pt"

      .. code-block:: bash

         sudo grubby --update-kernel ALL --remove-args="rhgb quiet"

#. Install various packages (Optional)

   .. code-block:: bash

      sudo dnf install bat btop neofetch neovim terminator slack

#. Install packages via Sofware store.

   - Yubico Authenticator
   - Visual Studio Code

#. Install extensions https://extensions.gnome.org/

   - Caffeine
   - Dash to Dock
   - Tactile
   - User Themes

#. Install themes & icons https://www.gnome-look.org/browse/

   - Nordic-v40
   - Bluish-Dark-Icons
   - Tango2

   .. code-block:: bash

      gsettings set org.gnome.desktop.interface gtk-theme "Nordic-v40"
      gsettings set org.gnome.desktop.wm.preferences theme "Nordic-v40"

   .. tip:: Install MS core fonts for clean font rendering.

      .. code-block:: bash

         sudo dnf install mscore-fonts

#. Install and update PIP. Install misc packages

   .. code-block:: bash

      sudo dnf install python3-pip

      pip install pip -U

      # add misc packages
      pip install ansible awscli pygments wheel

#. Add Sphinx build environment

   .. code-block:: bash

      pip install sphinx==7.4.7 docutils==0.20.1 sphinx_rtd_theme==2.0.0 sphinx-copybutton==0.5.2 pre-commit==3.8.0

      # F5 Theme
      pip install f5_sphinx_theme recommonmark sphinxcontrib.addmetahtml sphinxcontrib.nwdiag sphinxcontrib.blockdiag sphinxcontrib-websupport
      sudo dnf install graphviz

#. VNC (Server)

   Install vnc-server

   .. code-block:: bash

      sudo dnf install tigervnc-server

   Open Firewall

   .. code-block:: bash

      sudo firewall-cmd --add-service vnc-server --permanent
      sudo firewall-cmd --reload
      sudo firewall-cmd --list-all

   Map users to display and port numbers

   .. code-block:: bash

      sudo vim /etc/tigervnc/vncserver.users

      # ADD Newline with following for user vince
      :1=vince

   If Nvidia Disable Wayland

   .. code-block:: bash

      sudo vim /etc/gdm/custom.conf

      # Set and add following
      [daemon]
      WaylandEnable=False
      DefaultSession=gnome-xorg.desktop

   Enable vnc service

   .. code-block:: bash

       sudo systemctl enable --now vncserver@:1
       sudo systemctl status vncserver@:1

   Set the passwd for the vncpasswd

   .. code-block:: bash

      vncpasswd

#. VNC (Client - vncviewer/cli and remmina/gui)

   .. code-block:: bash

      sudo dnf install tigervnc remmina

   .. code-block:: bash

      vncviewer --shared bfg.lab.local:1

#. Remote Desktop Protocol (Server)

   .. code-block:: bash

      sudo dnf install xrdp

   .. code-block:: bash

      sudo firewall-cmd --add-service=rdp --permanent
      sudo firewall-cmd --reload
      sudo firewall-cmd --list-all

   .. code-block:: bash

      sudo systemctl enable --now xrdp
      sudo systemctl status xrdp

#. Modify sshd

   .. attention:: This assumes you've set up pki.

   .. code-block:: bash

      # modify following settings
      vim /etc/ssh/sshd_config
         PermitRootLogin no
         PasswordAuthentication no

      # reload service
      sudo systemctl restart sshd

      # Allow port 22
      sudo firewall-cmd --add-service=ssh --permanent
      sudo firewall-cmd --reload

#. Add user to wheel group **(If Needed)**

   .. code-block:: bash

      usermod -a -G wheel <user>

#. Use vi with visudo, permanently change editor

   .. code-block:: bash

      sudo EDITOR=vim visudo

   Add Following to visudo file, save and exit

   .. code-block:: bash

      Defaults editor=/usr/bin/vim

#. Modify sudo with NOPASSWD option

   .. code-block:: bash

      # Modify sudo with "visudo" and uncomment or modify the follow line
      %wheel  ALL=(ALL)       ALL
      # to
      %wheel  ALL=(ALL)       NOPASSWD: ALL

#. Set hostname

   .. code-block:: bash

      sudo hostnamectl set-hostname <new_host_name>

#. Use z shell (For corporate account go to next step).

   .. code-block:: bash

      chsh -s /bin/zsh

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
      git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME config --local status.showUntrackedFiles no

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

#. Configure OpenShift client tab complete

   - for zsh

     .. code-block:: bash

        oc completion zsh | sudo tee /usr/share/zsh/site-functions/_oc

     .. code-block:: bash

        # Add the following to ~/.zshrc
        source /usr/share/zsh/site-functions/_oc 2>/dev/null

   - for bash

     .. code-block:: bash

        oc completion bash | sudo tee /etc/bash_completion.d/oc_completion

#. Prefer IPv4. By default IPv6 addresses are preferred. Create /etc/gai.conf
   and change default priorities.

   .. code-block:: bash
      :emphasize-lines: 12

      sudo bash -c 'cat << EOF > /etc/gai.conf

      label  ::1/128       0
      label  ::/0          1
      label  2002::/16     2
      label ::/96          3
      label ::ffff:0:0/96  4
      precedence  ::1/128       50
      precedence  ::/0          40
      precedence  2002::/16     30
      precedence ::/96          20
      precedence ::ffff:0:0/96  60      # <=== Change this from 10 to 60 or higher
      EOF'

#. Install brave (I prefer this to the "Software" store)

   .. code-block:: bash

      sudo dnf install dnf-plugins-core
      sudo dnf config-manager --add-repo https://brave-browser-rpm-release.s3.brave.com/x86_64/
      sudo rpm --import https://brave-browser-rpm-release.s3.brave.com/brave-core.asc
      sudo dnf install brave-browser

   .. code-block:: bash

      # Add chromium corp policy to brave

      sudo mkdir -p /etc/brave/policies/managed
      sudo ln -s ../../../../usr/share/chromium/policies/recommended/00_gssapi.json 00_gssapi.json

#. Install NeoVIM from Source **(If Needed)**

   .. code-block:: bash

      sudo dnf install libtool autoconf automake cmake gcc gcc-c++ make pkgconfig unzip patch gettext curl
      git clone git@github.com:neovim/neovim.git ~/git/neovim
      cd ~/git/neovim
      make distclean
      make CMAKE_BUILD_TYPE=Release
      sudo make install

#. Install Terminator from Source **(If Needed)**

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

.. tip:: I ran into an issue where the default /tmp size caused an issue with
   oc mirror, needing more space. Removing this default puts /tmp back in root.

   Disable automatic mounting of tmpfs to /tmp by systemd.

   .. code-block:: bash

      systemctl mask tmp.mount

Upgrade Fedora
--------------

#. Update/Upgrade current running verion.

   .. code-block:: bash

      sudo dnf upgrade --refresh -y

#. Install the DNF-plugin-system-upgrade Package on Fedora.

   .. code-block:: bash

      sudo dnf install dnf-plugin-system-upgrade -y

#. Download desired Fedora release. In my example release 41.

   .. code-block:: bash

      sudo dnf system-upgrade download --releasever=41

   .. tip:: If you encounter conflicts during the upgrade, try adding
      ``--allowerasing`` option.

#. Upgrade and Reboot.

   .. code-block:: bash

      sudo dnf system-upgrade reboot

#. Confirm upgrade.

   .. code-block:: bash

      cat /etc/redhat-release

Upgrade RHEL
------------

#. Update/Upgrade current running verion.

   .. code-block:: bash

      sudo dnf upgrade --refresh -y

#. Install LEAPP

   .. code-block:: bash

      sudo dnf install leapp leapp-upgrade -y

#. Run LEAPP

   .. code-block:: bash

      sudo leapp upgrade

#. Reboot and confirm update

   .. code-block:: bash

      sudo reboot

   .. code-block:: bash

      cat /etc/redhat-release

#. Cleanup environment

   .. code-block:: bash

      sudo dnf autoremove
      sudo dnf clean all
      sudo dnf update --refresh -y

Logical Volume Management
-------------------------

Create the logical volume
~~~~~~~~~~~~~~~~~~~~~~~~~

#. Create the physical volume.

   .. code-block:: bash

      sudo pvcreate /dev/nvme1n1 /dev/nvme2n1

   Show newly created pv's

   .. code-block:: bash

      sudo pvs

#. Create the volume group.

   .. tip:: Use ``-s`` to set physicalextentsize Size[m|UNIT]

   .. code-block:: bash

      sudo vgcreate <VG_NAME> /dev/nvme1n1 /dev/nvme2n1

   Show newly created vg's

   .. code-block:: bash

      sudo vgs

#. Create the logical volume.

   .. tip:: Use ``-L`` to set Size[m|UNIT] or ``-l 100%FREE`` for percentage

   .. code-block:: bash

      sudo lvcreate -l 100%FREE --name <LV_NAME> <VG_NAME>

   Show newly created lv's

   .. code-block:: bash

      sudo lvs

#. Create the filesystem.

   .. tip:: Add mount to ``/etc/fstab``

   .. code-block:: bash

      mkfs.xfs /dev/<VG_NAME>/<LV_NAME>

      mount /dev/<VG_NAME>/<LV_NAME> <MOUNT_POINT>

Extend the logical volume
~~~~~~~~~~~~~~~~~~~~~~~~~

#. Create the physical volume.

   .. code-block:: bash

      sudo pvcreate /dev/nvme3n1

#. Extend the volume group.

   .. code-block:: bash

      sudo vgextend <VG_NAME> /dev/nvme3n1

#. Extend the logical volume.

   .. tip:: Use ``-L`` to set Size[m|UNIT] or ``-l 100%FREE`` for percentage

      If filesystem in place use ``-r`` to resizefs

   .. code-block:: bash

      sudo lvextend -l +100%FREE /dev/<VG_NAME>/<LV_NAME>

Remove the logical volume
~~~~~~~~~~~~~~~~~~~~~~~~~

#. Remove the logical volume.

   .. code-block:: bash

      sudo lvremove /dev/<VG_NAME>/<LV_NAME>

#. Remove the volume group.

   .. code-block:: bash

      sudo vgremove <VG_NAME>

#. Remove the physical volume.

   .. code-block:: bash

      sudo pvremove /dev/nvme1n1 /dev/nvme2n1
