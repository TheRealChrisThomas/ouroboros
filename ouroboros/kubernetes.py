import logging

from kubernetes import client, config

log = logging.getLogger(__name__)

def list_pods():
    config.load_kube_config()

    v1 = client.CoreV1Api()
    print("List of all pods that are running:")
    pods = v1.list_pod_for_all_namespaces(watch=False)
    for pod in pods:
        print("%s\t%s" % (pod.metadata.namespace, pod.metadata.name))

