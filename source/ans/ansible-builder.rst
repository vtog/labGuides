Ansible Builder
===============

When using ansible-builder part of the script is to always update the resulting
image. Customer needed way to leave the base image default.

Stop updating build
-------------------

#. Create the Containerfile file

   .. code-block:: bash

      ansible-builder create

#. Modify the Containerfile file by adding ``RUN sed -i /$PKGMGR update -y $PKGMGR_OPTS/d' /output/install-from-bindep``
   right before ``RUN /output/install-from-bindep && rm -rf /output/wheels``

   .. code-block:: console
      :emphasize-lines: 30

      ARG EE_BASE_IMAGE=registry.redhat.io/ansible-automation-platform-21/ee-minimal-rhel8:latest
      ARG EE_BUILDER_IMAGE=quay.io/ansible/ansible-builder:latest

      FROM $EE_BASE_IMAGE as galaxy
      ARG ANSIBLE_GALAXY_CLI_COLLECTION_OPTS=
      ARG ANSIBLE_GALAXY_CLI_ROLE_OPTS=
      USER root

      ADD _build /build
      WORKDIR /build

      RUN ansible-galaxy role install $ANSIBLE_GALAXY_CLI_ROLE_OPTS -r requirements.yml --roles-path "/usr/share/ansible/roles"
      RUN ANSIBLE_GALAXY_DISABLE_GPG_VERIFY=1 ansible-galaxy collection install $ANSIBLE_GALAXY_CLI_COLLECTION_OPTS -r requirements.yml --collections-path "/usr/share/ansible/collections"

      FROM $EE_BUILDER_IMAGE as builder

      COPY --from=galaxy /usr/share/ansible /usr/share/ansible

      ADD _build/requirements.txt requirements.txt
      ADD _build/bindep.txt bindep.txt
      RUN ansible-builder introspect --sanitize --user-pip=requirements.txt --user-bindep=bindep.txt --write-bindep=/tmp/src/bindep.txt --write-pip=/tmp/src/requirements.txt
      RUN assemble

      FROM $EE_BASE_IMAGE
      USER root

      COPY --from=galaxy /usr/share/ansible /usr/share/ansible

      COPY --from=builder /output/ /output/
      RUN sed -i '/$PKGMGR update -y $PKGMGR_OPTS/d' /output/install-from-bindep
      RUN /output/install-from-bindep && rm -rf /output/wheels
      LABEL ansible-execution-environment=true

#. Build the image

   .. code-block:: bash

      podman build -f context/Containerfile -t <name_of_image>

#. Run container and confirm version.

   .. code-block:: bash

      podman container run -it localhost/<name_of_image>:latest /bin/bash

   .. image:: ./images/ansibleversion.png

