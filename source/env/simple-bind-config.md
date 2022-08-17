# Simple BIND Config

1. Install bind
    ```console
    sudo dnf install bind bind-utils
    ```

2. Edit conf file
    ```console
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
    ```

3. Create directory structure
    ```console
    sudo mkdir -p /etc/named/zones
    ```

4. Create "named.conf.local"
    ```console
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
    ```

5.  Create forward zone file
    ```console
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
    ```

6. Create reverse zone file
    ```console
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
    ```

7. Start named
    ```console
    sudo systemctl enable --now named
    ```
