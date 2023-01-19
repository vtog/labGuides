Simple BIND Config
==================

#. Install bind

   .. code-block:: bash

      sudo dnf install bind bind-utils

#. Edit conf file

   .. code-block:: bash

      sudo vim /etc/named.conf
       
      # ADD ACL and include local host IP
      # and subnet for "virbr0"   
      acl "trusted" {
          127.0.0.1;
          192.168.1.72;
          192.168.122.1;
          192.168.122.0/24;
      };
       
      # Under "options" change the following
      listen-on port 53 { 127.0.0.1; 192.168.1.72; 192.168.122.1; };
      allow-query     { trusted; };
       
      # Add the following "include" to the end of the file
      include "/etc/named/named.conf.local";

#. Create directory structure

   .. code-block:: bash

      sudo mkdir -p /etc/named/zones

#. Create "named.conf.local"

   .. code-block:: bash

      cat << EOF | sudo tee /etc/named/named.conf.local
      zone "lab.local" {
          type master;
          file "/etc/named/zones/db.lab.local";
      };
      
      zone "122.168.192.in-addr.arpa" {
          type master;
          file "/etc/named/zones/db.122.168.192";
      };
      
      EOF

#. Create forward zone file

   .. code-block:: bash

      cat << EOF | sudo tee /etc/named/zones/db.lab.local
      \$TTL    604800
      @       IN      SOA     ns1.lab.local. admin.lab.local. (
                                    3         ; Serial
                               604800         ; Refresh
                                86400         ; Retry
                              2419200         ; Expire
                               604800 )       ; Negative Cache TTL
      
      ; name servers - NS records
              IN      NS      ns1.lab.local.
      
      ; name servers - A records
      ns1.lab.local.              IN      A      192.168.122.1
      
      ; 10.128.128.0/24 - A records
      host1.lab.local.            IN      A      192.168.122.101
      host2.lab.local.            IN      A      192.168.122.102
      mirror.lab.local.           IN      A      192.168.122.1
      
      api.acm.lab.local.          IN      A      192.168.122.245
      *.apps.acm.lab.local.       IN      A      192.168.122.220
      
      api.vtog1.lab.local.        IN      A      192.168.122.132
      *.apps.vtog1.lab.local.     IN      A      192.168.122.189
      
      EOF

#. Create reverse zone file

   .. code-block:: bash

      cat << EOF | sudo tee /etc/named/zones/db.122.168.192
      \$TTL    604800
      @       IN      SOA     ns1.lab.local. admin.lab.local. (
                                    3         ; Serial
                               604800         ; Refresh
                                86400         ; Retry
                              2419200         ; Expire
                               604800 )       ; Negative Cache TTL
      
      ; name servers - NS records
              IN      NS      ns1.lab.local.
      
      ; PTR Records
      1       IN      PTR     ns1.lab.local.    ; 192.168.122.1
      101     IN      PTR     host1.lab.local.  ; 192.168.122.101
      102     IN      PTR     host2.lab.local.  ; 192.168.122.102
      
      EOF

#. Start named

   .. code-block:: bash

      sudo systemctl enable --now named

