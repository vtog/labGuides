Sushy-Emulator
==============

Sushy is an emulator for Redfish, I'm using with KVM.

Containerize Sushy-Tools
------------------------

#. Get Sushy

   .. code-block:: bash

      sudo podman pull quay.io/metal3-io/sushy-tools:latest

#. Configure Sushy conf defaults.

   .. code-block:: bash
      :emphasize-lines: 9

      sudo mkdir -p /etc/sushy/
      cat << "EOF" | sudo tee /etc/sushy/sushy-emulator.conf
      SUSHY_EMULATOR_LISTEN_IP = u'0.0.0.0'
      SUSHY_EMULATOR_LISTEN_PORT = 8000
      SUSHY_EMULATOR_SSL_CERT = None
      SUSHY_EMULATOR_SSL_KEY = None
      SUSHY_EMULATOR_OS_CLOUD = None
      SUSHY_EMULATOR_LIBVIRT_URI = u'qemu:///system'
      SUSHY_EMULATOR_IGNORE_BOOT_DEVICE = False
      SUSHY_EMULATOR_BOOT_LOADER_MAP = {
          u'UEFI': {
              u'x86_64': u'/usr/share/OVMF/OVMF_CODE.secboot.fd'
          },
          u'Legacy': {
              u'x86_64': None
          }
      }
      EOF

   .. attention:: Be sure to set "SUSHY_EMULATOR_IGNORE_BOOT_DEVICE" to False
      for KVM.

#. Deploy Sushy container.

   .. code-block:: bash

      sudo podman create --net host --privileged --name sushy-emulator \
           -v "/etc/sushy":/etc/sushy -v "/var/run/libvirt":/var/run/libvirt \
           "quay.io/metal3-io/sushy-tools" sushy-emulator -i :: -p 8000 \
           --config /etc/sushy/sushy-emulator.conf

#. Generate systemd service

   .. code-block:: bash

      sudo podman generate systemd --name sushy-emulator --files
      sudo cp -Z container-sushy-emulator.service /etc/systemd/system/
      sudo systemctl daemon-reload
      sudo systemctl enable --now container-sushy-emulator.service

#. Allow port 8000 for service connectivity

   .. code-block:: bash

      sudo firewall-cmd --add-port=8000/tcp --permanent
      sudo firewall-cmd --reload
      sudo firewall-cmd --list-all

#. Test connectivity

   .. code-block:: bash

      curl http://192.168.1.72:8000/redfish/v1/Managers

Remove Sushy
------------

.. code-block:: bash

   sudo systemctl disable container-sushy-emulator.service
   sudo rm /etc/systemd/system/container-sushy-emulator.service
   sudo systemctl daemon-reload
   sudo podman stop sushy-emulator
   sudo podman rm sushy-emulator
   sudo podman rmi quay.io/metal3-io/sushy-tools
