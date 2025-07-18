Simple BIND Config
==================

#. Install bind

   .. code-block:: bash

      sudo dnf install bind bind-utils

#. Edit conf file

   .. code-block:: bash

      sudo vim /etc/named.conf

      # ADD ACL and include local host IP
      acl "trusted" {
          127.0.0.1;
          192.168.1.68;
          192.168.1.0/24;
          192.168.122.0/24;
          192.168.132.0/24;
          2600:1702:4c73:f110::/64;
          2600:1702:4c73:f111::/64;
      };

      # Under "options" change/add the following
      options {
        listen-on port 53 { 192.168.1.68; };
        listen-on-v6 port 53 { 2600:1702:4c73:f110::68; };
        allow-query { trusted; };

        # Enable/disable logging (see final step below)
        querylog no;

        recursion yes;

        forwarders { 192.168.1.53; };
      };

      # Add the following "include" to the end of the file for local zones
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
          file "/etc/named/zones/db.192.168.1";
      };
      zone "122.168.192.in-addr.arpa" {
          type master;
          file "/etc/named/zones/db.192.168.122";
      };
      zone "132.168.192.in-addr.arpa" {
          type master;
          file "/etc/named/zones/db.192.168.132";
      };
      zone "0.1.1.f.3.7.c.4.2.0.7.1.0.0.6.2.ip6.arpa" {
          type master;
          file "/etc/named/zones/db.2600.1702.4c73.f110";
      };
      zone "1.1.1.f.3.7.c.4.2.0.7.1.0.0.6.2.ip6.arpa" {
          type master;
          file "/etc/named/zones/db.2600.1702.4c73.f111";
      };
      EOF

#. Create forward zone file

   .. code-block:: bash

      cat << EOF | sudo tee /etc/named/zones/db.lab.local
      \$TTL    604800
      @     IN     SOA     ns1.lab.local. admin.lab.local. (
                              3         ; Serial
                         604800         ; Refresh
                          86400         ; Retry
                        2419200         ; Expire
                         604800         ; Negative Cache TTL
                         )

      ; name servers - NS records
            IN     NS      ns1.lab.local.

      ; name servers - A records
      ns1                 IN      A       192.168.1.68
                          IN      AAAA    2600:1702:4c73:f110::68

      ; 192.168.1.0/24 - A records
      bfg                 IN      A       192.168.1.72
      bfg                 IN      AAAA    2600:1702:4c73:f110::72
      mirror              IN      A       192.168.1.72
      mirror              IN      AAAA    2600:1702:4c73:f110::72

      ; 192.168.122.0/24 - A records
      rhel7-bastion       IN      A       192.168.122.7
      rhel7-bastion       IN      AAAA    600:1702:4c73:f111::7
      rhel8-bastion       IN      A       192.168.122.8
      rhel8-bastion       IN      AAAA    600:1702:4c73:f111::8
      rhel9-bastion       IN      A       192.168.122.9
      rhel9-bastion       IN      AAAA    600:1702:4c73:f111::9

      api.ocp1            IN      A       192.168.122.110
      api.ocp1            IN      AAAA    2600:1702:4c73:f111::110
      api-int.ocp1        IN      A       192.168.122.140
      api-int.ocp1        IN      AAAA    2600:1702:4c73:f111::110
      *.apps.ocp1         IN      A       192.168.122.111
      *.apps.ocp1         IN      AAAA    2600:1702:4c73:f111::111

      api.ocp2            IN      A       192.168.122.120
      api.ocp2            IN      AAAA    2600:1702:4c73:f111::120
      api-int.ocp2        IN      A       192.168.122.140
      api-int.ocp2        IN      AAAA    2600:1702:4c73:f111::120
      *.apps.ocp2         IN      A       192.168.122.121
      *.apps.ocp2         IN      AAAA    2600:1702:4c73:f111::121

      api.ocp3            IN      A       192.168.122.130
      api.ocp3            IN      AAAA    2600:1702:4c73:f111::130
      api-int.ocp3        IN      A       192.168.122.140
      api-int.ocp3        IN      AAAA    2600:1702:4c73:f111::130
      *.apps.ocp3         IN      A       192.168.122.131
      *.apps.ocp3         IN      AAAA    2600:1702:4c73:f111::131

      api.ocp4            IN      A       192.168.122.140
      api.ocp4            IN      AAAA    2600:1702:4c73:f111::140
      api-int.ocp4        IN      A       192.168.122.140
      api-int.ocp4        IN      AAAA    2600:1702:4c73:f111::140
      *.apps.ocp4         IN      A       192.168.122.141
      *.apps.ocp4         IN      AAAA    2600:1702:4c73:f111::141
      EOF

#. Create reverse zone file

   .. code-block:: bash

      cat << EOF | sudo tee /etc/named/zones/db.192.168.1
      \$TTL    604800
      @     IN     SOA     ns1.lab.local. admin.lab.local. (
                                    3         ; Serial
                               604800         ; Refresh
                                86400         ; Retry
                              2419200         ; Expire
                               604800         ; Negative Cache TTL
                               )

      ; name servers - NS records
            IN     NS      ns1.lab.local.

      ; PTR Records
      68      IN      PTR      ns1.lab.local.                   ; 192.168.1.68
      72      IN      PTR      bfg.lab.local.                   ; 192.168.1.72
      72      IN      PTR      mirror.lab.local.                ; 192.168.1.72

      140     IN      PTR      api.ocp4.lab.local.              ; 192.168.1.140
      140     IN      PTR      api-int.ocp4.lab.local.          ; 192.168.1.140

      72      IN      PTR      provisioner.ocp4.lab.local.      ; 192.168.1.72
      40      IN      PTR      host40.ocp4.lab.local.
      41      IN      PTR      host41.ocp4.lab.local.
      42      IN      PTR      host42.ocp4.lab.local.
      43      IN      PTR      host43.ocp4.lab.local.
      44      IN      PTR      host44.ocp4.lab.local.
      EOF

   .. code-block:: bash

      cat << EOF | sudo tee /etc/named/zones/db.192.168.122
      \$TTL    604800
      @     IN     SOA     ns1.lab.local. admin.lab.local. (
                                    3         ; Serial
                               604800         ; Refresh
                                86400         ; Retry
                              2419200         ; Expire
                               604800         ; Negative Cache TTL
                               )

      ; name servers - NS records
            IN     NS      ns1.lab.local.

      ; PTR Records
      7        IN      PTR      rhel7-bastion.lab.local.  ; 192.168.122.7
      8        IN      PTR      rhel8-bastion.lab.local.  ; 192.168.122.8
      9        IN      PTR      rhel9-bastion.lab.local.  ; 192.168.122.9

      110      IN      PTR      api.ocp1.lab.local.       ; 192.168.122.110
      110      IN      PTR      api-int.ocp1.lab.local.   ; 192.168.122.110
      120      IN      PTR      api.ocp2.lab.local.       ; 192.168.122.120
      120      IN      PTR      api-int.ocp2.lab.local.   ; 192.168.122.120
      130      IN      PTR      api.ocp3.lab.local.       ; 192.168.122.130
      130      IN      PTR      api-int.ocp3.lab.local.   ; 192.168.122.130
      140      IN      PTR      api.ocp4.lab.local.       ; 192.168.122.140
      140      IN      PTR      api-int.ocp4.lab.local.   ; 192.168.122.140
      EOF

   .. code-block:: bash

      cat << EOF | sudo tee /etc/named/zones/db.192.168.132
      \$TTL    604800
      @     IN     SOA     ns1.lab.local. admin.lab.local. (
                                    3         ; Serial
                               604800         ; Refresh
                                86400         ; Retry
                              2419200         ; Expire
                               604800         ; Negative Cache TTL
                               )

      ; name servers - NS records
            IN     NS      ns1.lab.local.

      ; PTR Records
      7        IN      PTR      rhel7-bastion.lab.local.  ; 192.168.132.7
      8        IN      PTR      rhel8-bastion.lab.local.  ; 192.168.132.8
      9        IN      PTR      rhel9-bastion.lab.local.  ; 192.168.132.9

      110      IN      PTR      api.ocp1.lab.local.       ; 192.168.132.110
      110      IN      PTR      api-int.ocp1.lab.local.   ; 192.168.132.110
      120      IN      PTR      api.ocp2.lab.local.       ; 192.168.132.120
      120      IN      PTR      api-int.ocp2.lab.local.   ; 192.168.132.120
      130      IN      PTR      api.ocp3.lab.local.       ; 192.168.132.130
      130      IN      PTR      api-int.ocp3.lab.local.   ; 192.168.132.130
      140      IN      PTR      api.ocp4.lab.local.       ; 192.168.132.140
      140      IN      PTR      api-int.ocp4.lab.local.   ; 192.168.132.140
      EOF

   .. code-block:: bash

      cat << EOF | sudo tee /etc/named/zones/db.2600.1702.4c73.f110
      \$TTL    604800
      @     IN     SOA     ns1.lab.local. admin.lab.local. (
                                    3         ; Serial
                               604800         ; Refresh
                                86400         ; Retry
                              2419200         ; Expire
                               604800         ; Negative Cache TTL
                               )

      ; name servers - NS records
            IN     NS      ns1.lab.local.

      $ORIGIN 0.0.0.0.0.0.0.0.0.0.0.0

      ; PTR Records
      2.7.0.0  IN      PTR      ns1.lab.local.
      2.7.0.0  IN      PTR      bfg.lab.local.
      2.7.0.0  IN      PTR      mirror.lab.local.
      EOF

   .. code-block:: bash

      cat << EOF | sudo tee /etc/named/zones/db.2600.1702.4c73.f111
      \$TTL    604800
      @     IN     SOA     ns1.lab.local. admin.lab.local. (
                                    3         ; Serial
                               604800         ; Refresh
                                86400         ; Retry
                              2419200         ; Expire
                               604800         ; Negative Cache TTL
                               )

      ; name servers - NS records
            IN     NS      ns1.lab.local.

      $ORIGIN 0.0.0.0.0.0.0.0.0.0.0.0

      ; PTR Records
      7.0.0.0      IN      PTR      rhel7-bastion.lab.local.
      8.0.0.0      IN      PTR      rhel8-bastion.lab.local.
      9.0.0.0      IN      PTR      rhel9-bastion.lab.local.

      0.1.1.0      IN      PTR      api.ocp1.lab.local.
      0.1.1.0      IN      PTR      api-int.ocp1.lab.local.
      0.2.1.0      IN      PTR      api.ocp2.lab.local.
      0.2.1.0      IN      PTR      api-int.ocp2.lab.local.
      0.3.1.0      IN      PTR      api.ocp3.lab.local.
      0.3.1.0      IN      PTR      api-int.ocp3.lab.local.
      0.4.1.0      IN      PTR      api.ocp4.lab.local.
      0.4.1.0      IN      PTR      api-int.ocp4.lab.local.
      EOF

#. Start named

   .. code-block:: bash

      sudo systemctl enable --now named

#. Update firewall for port 53

   .. code-block:: bash

      sudo firewall-cmd --add-service=dns --permanent
      sudo firewall-cmd --reload
      sudo firewall-cmd --list-all

#. To enable logging edit "/etc/named.conf" and add the "logging" section.

   .. code-block:: bash

      logging {
              channel default_debug {
                      file "data/named.run";
                      severity dynamic;
              };
              channel queries_log {
                      file "/var/log/named.query";
                      print-time yes;
                      print-category no;
                      print-severity no;
                      severity info;
              };
              category queries { queries_log; };
      };

   .. important:: Update fcontext of /var/log/named.query".

      .. code-block:: bash

         sudo semanage fcontext -a -t named_log_t "/var/log/named.query"
         sudo restorecon -v /var/log/named.query
