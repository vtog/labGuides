Simple Configuration
====================

Getting started
---------------

#. Useful NGINX Commands

   .. code-block:: bash

      sudo nginx -v            #version

      sudo nginx -V            #version & enabled modules

      sudo nginx -t            #config test

      sudo nginx -T            #full configuration dump

      sudo nginx -s reload     #reload signal

#. NGINX keeps it's conf in ``/etc/nginx`` directory

   A. Here's the default example of ``/etc/nginx/nginx.conf``

      .. code-block:: bash

         # For more information on configuration, see:
         #   * Official English Documentation: http://nginx.org/en/docs/
         #   * Official Russian Documentation: http://nginx.org/ru/docs/
         
         user nginx;
         worker_processes auto;
         error_log /var/log/nginx/error.log notice;
         pid /run/nginx.pid;
         
         # Load dynamic modules. See /usr/share/doc/nginx/README.dynamic.
         include /usr/share/nginx/modules/*.conf;
         
         events {
             worker_connections 1024;
         }
         
         http {
             log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                               '$status $body_bytes_sent "$http_referer" '
                               '"$http_user_agent" "$http_x_forwarded_for"';
         
             access_log  /var/log/nginx/access.log  main;
         
             sendfile            on;
             tcp_nopush          on;
             keepalive_timeout   65;
             types_hash_max_size 4096;
         
             include             /etc/nginx/mime.types;
             default_type        application/octet-stream;
         
             server {
                 listen       80;
                 listen       [::]:80;
                 server_name  _;
                 root         /usr/share/nginx/html;
         
                 # Load configuration files for the default server block.
                 include /etc/nginx/default.d/*.conf;
             }
         
             # Load modular configuration files from the /etc/nginx/conf.d directory.
             # See http://nginx.org/en/docs/ngx_core_module.html#include
             # for more information.
             include /etc/nginx/conf.d/*.conf;
         }

   B. Here's the default example of ``/etc/nginx/conf.d/default.conf``

      .. code-block:: bash

         server {
             listen 8080;
             server_name localhost;

             location / {
                 root /usr/share/nginx/html;
                 index index.html index.htm;
             }

             error_page 500 502 503 504 /50x.html;
             location = /50x.html {
                 root /usr/share/nginx/html;
             }
         }

Multi-Server setup
------------------

#. Create the directory structure

   .. code-block:: bash

      sudo mkdir -p /opt/services/app{1..3}

#. If needed open the local firewall

   .. code-block:: bash

      sudo firewall-cmd --add-port={9001..9003}/tcp --permanent
      sudo firewall-cmd reload
      sudo firewall-cmd --list-all

#. Create the following three index's in their corresponding directory.

   .. code-block:: html
      :caption: RED - APP 1

      <!doctype html>
      <html lang="en-US">

      <head>
      <link rel="icon" type="image/png"
          href="https://www.nginx.com/wp-content/uploads/2019/10/favicon-48-48.ico"
          sizes="48x48">

      <h1>This is my APP 1</h1>
      <style>
          body { background-color: #FF0000; }
      </style>
      <title>RED - APP 1</title>
      </head>

      </html>

   .. code-block:: html
      :caption: GREEN - APP 2

      <!doctype html>
      <html lang="en-US">

      <head>
      <link rel="icon" type="image/png"
          href="https://www.nginx.com/wp-content/uploads/2019/10/favicon-48-48.ico"
          sizes="48x48">

      <h1>This is my APP 2</h1>
      <style>
          body { background-color: #00FF00; }
      </style>
      <title>GREEN - APP 2</title>
      </head>

      </html>

   .. code-block:: html
      :caption: BLUE - APP 3

      <!doctype html>
      <html lang="en-US">

      <head>
      <link rel="icon" type="image/png"
          href="https://www.nginx.com/wp-content/uploads/2019/10/favicon-48-48.ico"
          sizes="48x48">

      <h1>This is my APP 3</h1>
      <style>
          body { background-color: #0000FF; }
      </style>
      <title>BLUE - APP 3</title>
      </head>

      </html>

#. Create ``/etc/nginx/conf.d/web.conf``

   .. code-block:: bash
      :caption: web.conf

      server {
      
          listen        9001;
          index   index.html;

          location / {
          root /opt/services/app1;
          }
      }

       server {

          listen        9002;
          index   index.html;

          location / {
          root /opt/services/app2;
          }
      }

       server {

          listen        9003;
          index   index.html;

          location / {
          root /opt/services/app3;
          }
      }

#. Test the config

   .. code-block:: bash

      sudo nginx -t

#. Load the config

   .. code-block:: bash

      sudo nginx -s reload
