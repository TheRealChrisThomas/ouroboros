from prometheus_client import Counter


def initialize_container_update_counter():
    """Initialize updated_containers_counter when ouroboros starts"""
    updated_containers_counter = Counter(
        'containers_updated', 'Count of containers updated', ['container'])
    updated_containers_counter.labels(container='all')
    return updated_containers_counter


def container_updates(label):
    """Increment container update count based on label"""
    updated_containers_counter.labels(container=label).inc()
