Self Contained Cluster How-To
=============================

OCP clusters require the ability to talk to a registry to validate locally
stored images. In a disconnected mode that may not always be possible. This
how-to will describe the steps necessary to build a local copy of all the
required cluster images on each cluster node. With the images stored locally,
on each node, the cluster can continue to operate without internet access.

Find, List and Copy Images
--------------------------

1. To view the list of required cluster images click here: 
   `v4.9.43 <https://mirror.openshift.com/pub/openshift-v4/clients/ocp/4.9.43/release.txt>`_.

   Download the images:

   .. code-block:: console

      curl https://mirror.openshift.com/pub/openshift-v4/clients/ocp/4.9.43/release.txt -o release-4.9.43.txt

   .. attention:: We're using v4.9.43 in this example. Simply change the
      version in the uri to match the desired version.

#. To get the list of images, do the following:

   .. code-block:: console

      grep openshift-release-dev release-4.9.43.txt | grep quay.io | awk '{print $2}' | grep -v From > images.lst

#. Now we need to add the Operator images to the list of requirements.

   .. code-block:: console

      oc adm catalog mirror registry.redhat.io/redhat/redhat-operator-index:v4.9 file:///local/index -a pull-secret.json --insecure --index-filter-by-os='linux/amd64' --manifests-only

   .. attention:: Change operator-index to match the major release of OCP.

   .. note:: A new directory called "manifests-redhat-operator-index-1665676536" was created in this example.

#. Show list of operators

   .. code-block:: console

      awk -F "/" '{print $2}' manifests-redhat-operator-index-1665676536/mapping.txt | sort | uniq

#. Create list of required opeator images
 
   .. note:: In our lab we'll focus on the ODF and Local Storage operators.
 
   .. code-block:: console
 
      grep odf4 manifests-redhat-operator-index-1665676536/mapping.txt | awk -F "=" '{print $1}' > operators.lst
 
      grep local-storage manifests-redhat-operator-index-1665676536/mapping.txt | awk -F "=" '{print $1}' >> operators.lst
 
#. Copy images.lst and oparators.lst to node

   .. code-block:: console

      scp *.lst core@192.168.122.31:~

#. Pull all the images into local store (/var/lib/containers/storage)

   .. important:: Errors may occur when running the for loops. I recommend
      running these commands twice. The second time should be much faster.

   .. warning:: Be patient! This can take a while depending on your internet
      connection and the number of required operators.

   First the release images:

   .. code-block:: console

      ssh core@192.168.122.31

      cd /home/core

      for image in `cat images.lst`; do sudo crictl pull $image; done;

   Now the operator images:

   .. code-block:: console
   
      for image in `cat operators.lst`; do sudo crictl pull $image; done;

#. Create the alternate location and copy the images

   .. code-block:: console

      sudo -s

      mkdir /home/core/images

      cd /var/lib/containers/storage

      cp -a overlay* /home/core/images/

   .. note:: Be patient!

#. After image copy finishes, exit back to primary host

   .. note:: If root (and you should be) you'll need to type "exit" twice

   .. code-block:: console

      exit

#. Sync alternate location with all nodes

   For this to work the private key will need to be copied to the primary node.
   In my example 192.168.122.31

   .. code-block:: console

      scp ~/.ssh/id_rsa core@192.168.122.31:~
   
   .. attention:: The location and key name may differ.

   SSH back to primary node

   .. code-block:: console

      ssh core@192.168.122.31

   Configure ssh access

   .. code-block:: console

      sudo mkdir /root/.ssh

      sudo mv ~/id_rsa /root/.ssh/

   Sync nodes

   .. code-block:: console

      sudo rsync -av /home/core/images core@1921.168.122.32:~

   .. important:: Repeat "rsync" step for each node in the cluster.

#. Create the MachineConfig yaml file to use additionalimagestores

   The following code block will update "/etc/containers/storage.conf" with
   this line "additionalimagestores = ["/home/core/images",]" on each node
   specified by the label.

   .. code-block:: yaml

      apiVersion: machineconfiguration.openshift.io/v1
      kind: MachineConfig
      metadata:
        labels:
          machineconfiguration.openshift.io/role: master
        name: 99-container-master-storage-conf
      spec:
        config:
          ignition:
            version: 3.2.0
          storage:
            files:
              - contents:
                  source: >-
                    data:text/plain;charset=utf-8;base64,IyBUaGlzIGZpbGUgaXMgZ2VuZXJhdGVkIGJ5IHRoZSBNYWNoaW5lIENvbmZpZyBPcGVyYXRvcidzIGNvbnRhaW5lcnJ1bnRpbWVjb25maWcgY29udHJvbGxlci4KIwojIHN0b3JhZ2UuY29uZiBpcyB0aGUgY29uZmlndXJhdGlvbiBmaWxlIGZvciBhbGwgdG9vbHMKIyB0aGF0IHNoYXJlIHRoZSBjb250YWluZXJzL3N0b3JhZ2UgbGlicmFyaWVzCiMgU2VlIG1hbiA1IGNvbnRhaW5lcnMtc3RvcmFnZS5jb25mIGZvciBtb3JlIGluZm9ybWF0aW9uCiMgVGhlICJjb250YWluZXIgc3RvcmFnZSIgdGFibGUgY29udGFpbnMgYWxsIG9mIHRoZSBzZXJ2ZXIgb3B0aW9ucy4KW3N0b3JhZ2VdCgojIERlZmF1bHQgU3RvcmFnZSBEcml2ZXIKZHJpdmVyID0gIm92ZXJsYXkiCgojIFRlbXBvcmFyeSBzdG9yYWdlIGxvY2F0aW9uCnJ1bnJvb3QgPSAiL3Zhci9ydW4vY29udGFpbmVycy9zdG9yYWdlIgoKIyBQcmltYXJ5IFJlYWQvV3JpdGUgbG9jYXRpb24gb2YgY29udGFpbmVyIHN0b3JhZ2UKZ3JhcGhyb290ID0gIi92YXIvbGliL2NvbnRhaW5lcnMvc3RvcmFnZSIKCltzdG9yYWdlLm9wdGlvbnNdCiMgU3RvcmFnZSBvcHRpb25zIHRvIGJlIHBhc3NlZCB0byB1bmRlcmx5aW5nIHN0b3JhZ2UgZHJpdmVycwoKIyBBZGRpdGlvbmFsSW1hZ2VTdG9yZXMgaXMgdXNlZCB0byBwYXNzIHBhdGhzIHRvIGFkZGl0aW9uYWwgUmVhZC9Pbmx5IGltYWdlIHN0b3JlcwojIE11c3QgYmUgY29tbWEgc2VwYXJhdGVkIGxpc3QuCmFkZGl0aW9uYWxpbWFnZXN0b3JlcyA9IFsiL2hvbWUvY29yZS9pbWFnZXMiLF0KCiMgU2l6ZSBpcyB1c2VkIHRvIHNldCBhIG1heGltdW0gc2l6ZSBvZiB0aGUgY29udGFpbmVyIGltYWdlLiAgT25seSBzdXBwb3J0ZWQgYnkKIyBjZXJ0YWluIGNvbnRhaW5lciBzdG9yYWdlIGRyaXZlcnMuCnNpemUgPSAiIgoKIyBSZW1hcC1VSURzL0dJRHMgaXMgdGhlIG1hcHBpbmcgZnJvbSBVSURzL0dJRHMgYXMgdGhleSBzaG91bGQgYXBwZWFyIGluc2lkZSBvZgojIGEgY29udGFpbmVyLCB0byBVSURzL0dJRHMgYXMgdGhleSBzaG91bGQgYXBwZWFyIG91dHNpZGUgb2YgdGhlIGNvbnRhaW5lciwgYW5kCiMgdGhlIGxlbmd0aCBvZiB0aGUgcmFuZ2Ugb2YgVUlEcy9HSURzLiAgQWRkaXRpb25hbCBtYXBwZWQgc2V0cyBjYW4gYmUgbGlzdGVkCiMgYW5kIHdpbGwgYmUgaGVlZGVkIGJ5IGxpYnJhcmllcywgYnV0IHRoZXJlIGFyZSBsaW1pdHMgdG8gdGhlIG51bWJlciBvZgojIG1hcHBpbmdzIHdoaWNoIHRoZSBrZXJuZWwgd2lsbCBhbGxvdyB3aGVuIHlvdSBsYXRlciBhdHRlbXB0IHRvIHJ1biBhCiMgY29udGFpbmVyLgojCiMgcmVtYXAtdWlkcyA9IDA6MTY2ODQ0MjQ3OTo2NTUzNgojIHJlbWFwLWdpZHMgPSAwOjE2Njg0NDI0Nzk6NjU1MzYKCiMgUmVtYXAtVXNlci9Hcm91cCBpcyBhIG5hbWUgd2hpY2ggY2FuIGJlIHVzZWQgdG8gbG9vayB1cCBvbmUgb3IgbW9yZSBVSUQvR0lECiMgcmFuZ2VzIGluIHRoZSAvZXRjL3N1YnVpZCBvciAvZXRjL3N1YmdpZCBmaWxlLiAgTWFwcGluZ3MgYXJlIHNldCB1cCBzdGFydGluZwojIHdpdGggYW4gaW4tY29udGFpbmVyIElEIG9mIDAgYW5kIHRoZSBhIGhvc3QtbGV2ZWwgSUQgdGFrZW4gZnJvbSB0aGUgbG93ZXN0CiMgcmFuZ2UgdGhhdCBtYXRjaGVzIHRoZSBzcGVjaWZpZWQgbmFtZSwgYW5kIHVzaW5nIHRoZSBsZW5ndGggb2YgdGhhdCByYW5nZS4KIyBBZGRpdGlvbmFsIHJhbmdlcyBhcmUgdGhlbiBhc3NpZ25lZCwgdXNpbmcgdGhlIHJhbmdlcyB3aGljaCBzcGVjaWZ5IHRoZQojIGxvd2VzdCBob3N0LWxldmVsIElEcyBmaXJzdCwgdG8gdGhlIGxvd2VzdCBub3QteWV0LW1hcHBlZCBjb250YWluZXItbGV2ZWwgSUQsCiMgdW50aWwgYWxsIG9mIHRoZSBlbnRyaWVzIGhhdmUgYmVlbiB1c2VkIGZvciBtYXBzLgojCiMgcmVtYXAtdXNlciA9ICJzdG9yYWdlIgojIHJlbWFwLWdyb3VwID0gInN0b3JhZ2UiCgpbc3RvcmFnZS5vcHRpb25zLnRoaW5wb29sXQojIFN0b3JhZ2UgT3B0aW9ucyBmb3IgdGhpbnBvb2wKCiMgYXV0b2V4dGVuZF9wZXJjZW50IGRldGVybWluZXMgdGhlIGFtb3VudCBieSB3aGljaCBwb29sIG5lZWRzIHRvIGJlCiMgZ3Jvd24uIFRoaXMgaXMgc3BlY2lmaWVkIGluIHRlcm1zIG9mICUgb2YgcG9vbCBzaXplLiBTbyBhIHZhbHVlIG9mIDIwIG1lYW5zCiMgdGhhdCB3aGVuIHRocmVzaG9sZCBpcyBoaXQsIHBvb2wgd2lsbCBiZSBncm93biBieSAyMCUgb2YgZXhpc3RpbmcKIyBwb29sIHNpemUuCiMgYXV0b2V4dGVuZF9wZXJjZW50ID0gIjIwIgoKIyBhdXRvZXh0ZW5kX3RocmVzaG9sZCBkZXRlcm1pbmVzIHRoZSBwb29sIGV4dGVuc2lvbiB0aHJlc2hvbGQgaW4gdGVybXMKIyBvZiBwZXJjZW50YWdlIG9mIHBvb2wgc2l6ZS4gRm9yIGV4YW1wbGUsIGlmIHRocmVzaG9sZCBpcyA2MCwgdGhhdCBtZWFucyB3aGVuCiMgcG9vbCBpcyA2MCUgZnVsbCwgdGhyZXNob2xkIGhhcyBiZWVuIGhpdC4KIyBhdXRvZXh0ZW5kX3RocmVzaG9sZCA9ICI4MCIKCiMgYmFzZXNpemUgc3BlY2lmaWVzIHRoZSBzaXplIHRvIHVzZSB3aGVuIGNyZWF0aW5nIHRoZSBiYXNlIGRldmljZSwgd2hpY2gKIyBsaW1pdHMgdGhlIHNpemUgb2YgaW1hZ2VzIGFuZCBjb250YWluZXJzLgojIGJhc2VzaXplID0gIjEwRyIKCiMgYmxvY2tzaXplIHNwZWNpZmllcyBhIGN1c3RvbSBibG9ja3NpemUgdG8gdXNlIGZvciB0aGUgdGhpbiBwb29sLgojIGJsb2Nrc2l6ZT0iNjRrIgoKIyBkaXJlY3Rsdm1fZGV2aWNlIHNwZWNpZmllcyBhIGN1c3RvbSBibG9jayBzdG9yYWdlIGRldmljZSB0byB1c2UgZm9yIHRoZQojIHRoaW4gcG9vbC4gUmVxdWlyZWQgaWYgeW91IHNldHVwIGRldmljZW1hcHBlcgojIGRpcmVjdGx2bV9kZXZpY2UgPSAiIgoKIyBkaXJlY3Rsdm1fZGV2aWNlX2ZvcmNlIHdpcGVzIGRldmljZSBldmVuIGlmIGRldmljZSBhbHJlYWR5IGhhcyBhIGZpbGVzeXN0ZW0KIyBkaXJlY3Rsdm1fZGV2aWNlX2ZvcmNlID0gIlRydWUiCgojIGZzIHNwZWNpZmllcyB0aGUgZmlsZXN5c3RlbSB0eXBlIHRvIHVzZSBmb3IgdGhlIGJhc2UgZGV2aWNlLgojIGZzPSJ4ZnMiCgojIGxvZ19sZXZlbCBzZXRzIHRoZSBsb2cgbGV2ZWwgb2YgZGV2aWNlbWFwcGVyLgojIDA6IExvZ0xldmVsU3VwcHJlc3MgMCAoRGVmYXVsdCkKIyAyOiBMb2dMZXZlbEZhdGFsCiMgMzogTG9nTGV2ZWxFcnIKIyA0OiBMb2dMZXZlbFdhcm4KIyA1OiBMb2dMZXZlbE5vdGljZQojIDY6IExvZ0xldmVsSW5mbwojIDc6IExvZ0xldmVsRGVidWcKIyBsb2dfbGV2ZWwgPSAiNyIKCiMgbWluX2ZyZWVfc3BhY2Ugc3BlY2lmaWVzIHRoZSBtaW4gZnJlZSBzcGFjZSBwZXJjZW50IGluIGEgdGhpbiBwb29sIHJlcXVpcmUgZm9yCiMgbmV3IGRldmljZSBjcmVhdGlvbiB0byBzdWNjZWVkLiBWYWxpZCB2YWx1ZXMgYXJlIGZyb20gMCUgLSA5OSUuCiMgVmFsdWUgMCUgZGlzYWJsZXMKIyBtaW5fZnJlZV9zcGFjZSA9ICIxMCUiCgojIG1rZnNhcmcgc3BlY2lmaWVzIGV4dHJhIG1rZnMgYXJndW1lbnRzIHRvIGJlIHVzZWQgd2hlbiBjcmVhdGluZyB0aGUgYmFzZQojIGRldmljZS4KIyBta2ZzYXJnID0gIiIKCiMgbW91bnRvcHQgc3BlY2lmaWVzIGV4dHJhIG1vdW50IG9wdGlvbnMgdXNlZCB3aGVuIG1vdW50aW5nIHRoZSB0aGluIGRldmljZXMuCiMgbW91bnRvcHQgPSAiIgoKIyB1c2VfZGVmZXJyZWRfcmVtb3ZhbCBNYXJraW5nIGRldmljZSBmb3IgZGVmZXJyZWQgcmVtb3ZhbAojIHVzZV9kZWZlcnJlZF9yZW1vdmFsID0gIlRydWUiCgojIHVzZV9kZWZlcnJlZF9kZWxldGlvbiBNYXJraW5nIGRldmljZSBmb3IgZGVmZXJyZWQgZGVsZXRpb24KIyB1c2VfZGVmZXJyZWRfZGVsZXRpb24gPSAiVHJ1ZSIKCiMgeGZzX25vc3BhY2VfbWF4X3JldHJpZXMgc3BlY2lmaWVzIHRoZSBtYXhpbXVtIG51bWJlciBvZiByZXRyaWVzIFhGUyBzaG91bGQKIyBhdHRlbXB0IHRvIGNvbXBsZXRlIElPIHdoZW4gRU5PU1BDIChubyBzcGFjZSkgZXJyb3IgaXMgcmV0dXJuZWQgYnkKIyB1bmRlcmx5aW5nIHN0b3JhZ2UgZGV2aWNlLgojIHhmc19ub3NwYWNlX21heF9yZXRyaWVzID0gIjAiCg==
                mode: 420
                overwrite: true
                path: /etc/containers/storage.conf

   .. attention:: This will apply to "masters" only. To apply to "workers" add or change the label.

#. Apply the previously created MachineConfig to the cluster

   .. code-block:: console

      oc apply -f 99-container-master-storage-conf.yaml

   .. warning:: This will cause all master nodes to reboot.

#. Confirm mcp is done updating the MachineConfig

   .. code-block:: console

      oc get mcp

   .. note:: When all nodes are finished they will show "UPDATED: True" and 
      "UPDATING: False"

   .. image:: images/ocgetmcp.png

#. Disabling the default OperatorHub sources

   .. code-block:: console

      oc patch OperatorHub cluster --type json -p '[{"op": "add", "path": "/spec/disableAllDefaultSources", "value": true}]'

#. Modifying the global cluster pull secret to disable remote health reporting

   Download the global cluster pull secret

   .. code-block:: console

      oc extract secret/pull-secret -n openshift-config --to=.

   Edit/remove the "cloud.openshift.com" JSON entry from the pull secret

   .. code-block:: console

      "cloud.openshift.com":{"auth":"<hash>","email":"<email_address>"}

   Update the global cluset pull secret

   .. code-block:: console

      oc set data secret/pull-secret -n openshift-config --from-file=.dockerconfigjson=<pull_secret_location> 

#. Confirming the image store

   .. hint:: A good way to validate the images are where expected is with the
      use of SSH and podman. You'll notice a read-only column in the images
      list. The alternate image store *(/home/core/images)* is read-only,
      "true". And the default image store *(/var/lib/containers/storage)* is
      NOT read-only, "false".

   Lets confirm the number of images. The count for "true" should be the same
   on each node.

   .. code-block:: console

      ssh core@192.168.122.31 sudo podman images | grep true | wc -l
      ssh core@192.168.122.32 sudo podman images | grep true | wc -l
      ssh core@192.168.122.33 sudo podman images | grep true | wc -l

   .. image:: images/podmantruecount.png

