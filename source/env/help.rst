Helpful Commands
================

I'm always searching for ways to do the following:

General Linux Commands
----------------------

vi command to remove trailing white space in file:

.. code-block:: bash

   :%s/\s\+$//e

sed command to remove trailing white space in file:

.. code-block:: bash

   sed -i -e 's/\s\+$//' <file_name>

Search file for entry starting with some name and delete line. In my example
I'm searching the "~/.ssh/known_hosts" file for lines that start with "host51"
and deleting that line.

.. code-block:: bash

   sed -i -e '/^host51/d' ~/.ssh/known_hosts

Create key/cert pair with OpenSSL
---------------------------------

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
