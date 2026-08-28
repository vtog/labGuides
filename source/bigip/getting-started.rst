Getting Started
===============

LAB Passwords
-------------

I'm always doing the following TMSH commands to get started:

#. Disable password policy enforcement (It's a LAB)

   .. code-block:: bash

      tmsh modify auth password-policy policy-enforcement disabled

#. Set admin and root passwords

   .. code-block:: bash

      tmsh modify auth password admin

      tmsh modify auth password root

#. Allow admin SSH access

   .. code-block:: bash

     tmsh modify auth user admin shell bash
