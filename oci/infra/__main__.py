"""A OCI Python Base Infra Pulumi program"""

import pulumi
from network import Network

# -----------------------------------------------------------
# Configuration
# -----------------------------------------------------------
oci_config = pulumi.Config("oci")
config = pulumi.Config()

# Instantiate the Network class to create network resources.
network = Network(oci_config, config)
