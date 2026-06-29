NGINX One
=========

Agent
-----

#. Manually installing the NGINX Agent on NGINX Plus and connect to NGINX One

   .. note:: Be sure to replace 'data-plane-key' with your key and the 'config-
      sync-group' with your group.

   .. code-block:: bash

      curl https://agent.connect.nginx.com/nginx-agent/install | DATA_PLANE_KEY='data-plane-key' sh -s -- -y -c <config-sync-group>
