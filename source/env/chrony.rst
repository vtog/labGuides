Chrony
======

Simple chrony config for any environment.

.. note:: Only changes are the allow and bindaddress settings. Be sure to add
   any local time source server.

.. tip:: Unrem "#local stratum 10" and add "orphan" to the end of the line.
   This allows clients in a disconnected environment to use this time source
   even when the time source can't sync time.

.. code-block:: bash

   # Use public servers from the pool.ntp.org project.
   # Please consider joining the pool (https://www.pool.ntp.org/join.html).
   pool 2.fedora.pool.ntp.org iburst

   # Use NTP servers from DHCP.
   sourcedir /run/chrony-dhcp

   # Record the rate at which the system clock gains/losses time.
   driftfile /var/lib/chrony/drift

   # Allow the system clock to be stepped in the first three updates
   # if its offset is larger than 1 second.
   makestep 1.0 3

   # Enable kernel synchronization of the real-time clock (RTC).
   rtcsync

   # Enable hardware timestamping on all interfaces that support it.
   #hwtimestamp *

   # Increase the minimum number of selectable sources required to adjust
   # the system clock.
   #minsources 2

   # Allow NTP client access from local network.
   allow 192.168.0.0/16
   bindaddress 192.168.1.68

   # Serve time even if not synchronized to a time source.
   local stratum 10 orphan

   # Require authentication (nts or key option) for all NTP sources.
   #authselectmode require

   # Specify file containing keys for NTP authentication.
   #keyfile /etc/chrony.keys

   # Save NTS keys and cookies.
   ntsdumpdir /var/lib/chrony

   # Insert/delete leap seconds by slewing instead of stepping.
   #leapsecmode slew

   # Set the TAI-UTC offset of the system clock.
   leapseclist /usr/share/zoneinfo/leap-seconds.list

   # Specify directory for log files.
   logdir /var/log/chrony

   # Select which information is logged.
   #log measurements statistics tracking
