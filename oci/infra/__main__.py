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

# Outputs
pulumi.export("vcn_id", network.vcn.id)
pulumi.export("private_subnet_id", network.private_subnet.id)
pulumi.export("public_subnet_id", network.public_subnet.id)
pulumi.export("internet_gateway_id", network.internet_gateway.id)
