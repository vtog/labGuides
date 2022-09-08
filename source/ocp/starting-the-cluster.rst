Starting the Cluster
====================

Bringing the cluster back up is much more simple than the shutdown procedure.
You just have to start nodes in the right order for the best results.

Start your master nodes
-----------------------
*"master 1 - 3"*

Once they have booted we can check that they are healthy using :code:`oc get nodes`

.. note:: All nodes should be in a ready state before continuing on to your infra
   nodes.

Start your infra nodes
----------------------
*"worker 7 - 9"*

Once your infra nodes have booted you can ensure the infra nodes are showing
in a ready state :code:`oc get nodes`, and that :code:`oc get pods --all-namespaces`
shows the logging, metrics, router and registry pods have started and are healthy.

Start your worker nodes
-----------------------
*"worker 4 - 6"*

Once your worker nodes have booted you can ensure that all nodes are showing in
a ready state with :code:`oc get nodes`. Refer to the health check documentation
for a more in-depth set of checks.

Start your applications
-----------------------
Now that your cluster has started and is healthy, you can now start your
application workload. If you chose to simply shutdown your worker nodes without
draining workload then your applications will be restarting on the nodes they
were previously located, otherwise you will need to increase the number of
replica's or *'uncordon'* nodes depending on the approach you took.

Health Check
------------
Finally, check that your application pods have started correctly
:code:`oc get pods --all-namespaces` and perform any checks that may be
necessary on your application to prove that it is available and healthy. 
