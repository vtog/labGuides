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
          192.168.1.0/24;
          192.168.122.0/24;
          192.168.132.0/24;
          2600:1702:4c73:f110::/64;
          2600:1702:4c73:f111::/64;

      };
       
      # Under "options" change the following
      listen-on port 53 { any; };
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
      zone "1.168.192.in-addr.arpa" {
          type master;
          file "/etc/named/zones/db.1.168.192";
      };
      zone "122.168.192.in-addr.arpa" {
          type master;
          file "/etc/named/zones/db.122.168.192";
      };
      zone "132.168.192.in-addr.arpa" {
          type master;
          file "/etc/named/zones/db.132.168.192";
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
      ns1.lab.local.              IN      A      192.168.1.72
      
      ; 192.168.1.0/24 - A records
      bfg.lab.local.              IN      A      192.168.1.72
      mirror.lab.local.           IN      A      192.168.1.72

      ; 192.168.122.0/24 - A records
      rhel7-bastion.lab.local.    IN      A      192.168.122.7
      rhel8-bastion.lab.local.    IN      A      192.168.122.8
      rhel9-bastion.lab.local.    IN      A      192.168.122.9

      api.ocp1.lab.local.         IN      A      192.168.122.110
      api-int.ocp1.lab.local.     IN      A      192.168.122.110
      *.apps.ocp1.lab.local.      IN      A      192.168.122.111

      api.ocp2.lab.local.         IN      A      192.168.122.120
      api-int.ocp2.lab.local.     IN      A      192.168.122.120
      *.apps.ocp2.lab.local.      IN      A      192.168.122.121

      api.ocp3.lab.local.         IN      A      192.168.122.130
      api-int.ocp3.lab.local.     IN      A      192.168.122.130
      *.apps.ocp3.lab.local.      IN      A      192.168.122.131

      api.ocp4.lab.local.         IN      A      192.168.122.140
      api-int.ocp4.lab.local.     IN      A      192.168.122.140    
      *.apps.ocp4.lab.local.      IN      A      192.168.122.141

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
      7       IN      PTR     rhel7-bastion.lab.local.  ; 192.168.122.7
      8       IN      PTR     rhel8-bastion.lab.local.  ; 192.168.122.8
      9       IN      PTR     rhel9-bastion.lab.local.  ; 192.168.122.9

      110     IN      PTR     api.ocp1.lab.local.       ; 192.168.122.110
      110     IN      PTR     api-int.ocp1.lab.local.   ; 192.168.122.110
      120     IN      PTR     api.ocp2.lab.local.       ; 192.168.122.120
      120     IN      PTR     api-int.ocp2.lab.local.   ; 192.168.122.120
      130     IN      PTR     api.ocp3.lab.local.       ; 192.168.122.130
      130     IN      PTR     api-int.ocp3.lab.local.   ; 192.168.122.130
      140     IN      PTR     api.ocp4.lab.local.       ; 192.168.122.140
      140     IN      PTR     api-int.ocp4.lab.local.   ; 192.168.122.140
      
      EOF

#. Start named

   .. code-block:: bash

      sudo systemctl enable --now named

