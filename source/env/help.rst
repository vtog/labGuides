Helpful Commands
================

I'm always searching for ways to do the following:

General Linux Commands
----------------------

vi command to remove trailing white space in file:

.. code-block:: bash

   :%s/\s\+$//e

vi command to remove blank lines:

.. code-block:: bash

   :g/^$/d

sed command to remove trailing white space in file:

.. code-block:: bash

   sed -i -e 's/\s\+$//' <file_name>

Search file for entry starting with some name and delete line. In my example
I'm searching the "~/.ssh/known_hosts" file for lines that start with "host51"
and deleting that line.

.. code-block:: bash

   sed -i -e '/^host51/d' ~/.ssh/known_hosts

Append rootCA to file indenting each line with two spaces.

.. code-block:: bash

   echo "additionalTrustBundle: |" >> install-config.yaml
   sed -e 's/^/  /' /mirror/ocp4/quay-rootCA/rootCA.pem >> install-config.yaml

Force Reboot (Last Resort)

.. code-block:: bash

   sudo systemctl reboot --force --force

Create auth key
---------------

.. note::

   **-b bits**

   Specifies the number of bits in the key to create. For RSA keys, the minimum
   size is 1024 bits and the default is 3072 bits. Generally, 3072 bits is
   considered sufficient. For ECDSA keys, the -b flag determines the key length
   by selecting from one of three elliptic curve sizes: 256, 384 or 521 bits.
   Attempting to use bit lengths other than these three values for ECDSA keys
   will fail. ECDSA-SK, Ed25519 and Ed25519-SK keys have a fixed length and the
   -b flag will be ignored.

   **-t ecdsa | ecdsa-sk | ed25519 | ed25519-sk | rsa**

   Specifies the type of key to create. The possible values are “ecdsa”,
   “ecdsa-sk”, “ed25519 (the default),” “ed25519-sk”, or “rsa”.

.. code-block:: bash

   ssh-keygen -t rsa -b 4096

Create key/cert pair with OpenSSL
---------------------------------

.. tip:: For binding more then one key for auth, create ~/.ssh/config file
   with following info. This will check both keys (or more) when authenticating
   to all hosts.

   .. code-block:: bash

      Host *
        AddKeysToAgent yes
        IdentityFile ~/.ssh/id_rsa
        IdentityFile ~/.ssh/gitea

#. Run the following command to create the private key

   .. code-block:: bash

      openssl genrsa -out training.key 4096

#. Run the following command to generate CSR

   .. code-block:: bash

      openssl req -new \
      -subj "/C=US/ST=North Carolina/L=Raleigh/O=Red Hat/CN=todo-https.apps.ocp4.example.com" \
      -key training.key -out training.csr

#. Run the following command to generate cert

   .. code-block:: bash

      openssl x509 -req -in training.csr \
      -passin file:passphrase.txt \
      -CA training-CA.pem -CAkey training-CA.key -CAcreateserial \
      -out training.crt -days 1825 -sha256 -extfile training.ext

GIT
---

#. Add a new repo

   - Create a directory to contain the project.
   - Go into the new directory.
   - Type "git init".
   - Add some files.
   - Type "git add ." to add the files.
   - Type "git commit -m "note"".

#. Sync Rep with Github

   - Go to github
   - Click new repo
   - Name repo (I use name of directory created above.)
   - Click create repo
   - Type "git remote add origin git@github.com:username/new_repo"
   - Type "git branch -M main"
   - Type "git push -u origin main"
