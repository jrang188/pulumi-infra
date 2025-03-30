"""A OCI Python Base Infra Pulumi program"""

import pulumi
from network import Network
from compute import ComputeInstance

# -----------------------------------------------------------
# Configuration
# -----------------------------------------------------------
oci_config = pulumi.Config("oci")
config = pulumi.Config()

# Instantiate the Network class to create network resources.
network = Network(oci_config, config)

# Instantiate the ComputeInstance class to create ARM-based VM for K3S Server
k3s_server = ComputeInstance(
    oci_config,
    config,
    instance_name="k3s-server",
    instance_ocpus=4,
    instance_memory_in_gbs=24,
    subnet_id=network.public_subnet.id,
    amd64_cpu=False,  # Use ARM-based VM for K3S Server
).output()
