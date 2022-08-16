# OCP Cert Expiry and Resolution

In the event that oauth is down, indicated by "connection refused" running any
OC command against the API. The issue is most likely caused by an expired
internal cluster certificate. Internal cluster certs have an expiry of 30d.
Under normal circumstances these certs are auto renewed. By running the
following commands you can confirm expired certs and resolve the issue.

1. SSH to any master node.
   ```console
   ssh core@master1
   sudo -s
   ```
2. Export recovery KUBECONFIG for local cluster management.
   ```console
   export KUBECONFIG=/etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/node-kubeconfigs/localhost-recovery.kubeconfig
   ```
3. View pending CSR's (should see several in the pending state).
   ```console
   oc get csr
   ```
4. Approve all CSR's.
   ```yaml
   oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs --no-run-if-empty oc adm certificate approve
   ```
5. Repeat steps 3 and 4 until all pending CSR's are approved.

**NOTES**
1. Download for review csr-signer cert and key.
   ```console
   oc extract secret/csr-signer -n openshift-kube-controller-manager --to /home/user/ --confirm
   ```
2. View csr-signer cert (this shows the 30d expiry)
   ```console
   openssl x509 -text -noout -in /home/user/tls.crt
   ```
