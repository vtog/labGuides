OCP Cert Expiry and Resolution
==============================

In the event that oauth is down, indicated by "connection refused" running any
OC command against the API. The issue is most likely caused by an expired
internal cluster certificate. Internal cluster certs have an expiry of 30d.
Under normal circumstances these certs are auto renewed. By running the
following commands you can confirm expired certs and resolve the issue.

#. SSH to any master node.

   .. code-block:: console

      ssh core@master1
      sudo -s

#. Export recovery KUBECONFIG for local cluster management.

   .. code-block:: console

      export KUBECONFIG=/etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/node-kubeconfigs/localhost-recovery.kubeconfig

#. View pending CSR's (should see several in the pending state).

   .. code-block:: console

      oc get csr

#. Approve all CSR's.

   .. code-block:: yaml
 
      oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs --no-run-if-empty oc adm certificate approve

#. Repeat steps 3 and 4 until all pending CSR's are approved.

NOTES
-----
#. Download for review csr-signer cert and key.

   .. code-block:: console

      oc extract secret/csr-signer -n openshift-kube-controller-manager --to /home/user/ --confirm

#. View csr-signer cert (this shows the 30d expiry)

   .. code-block:: console

      openssl x509 -text -noout -in /home/user/tls.crt

