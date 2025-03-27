"""A OCI Python Pulumi program"""

import pulumi
import pulumi_oci as oci

oci_config = pulumi.Config("oci")
config = pulumi.Config()

tenancy_ocid = oci_config.require_secret("tenancyOcid")
compartment_ocid = oci_config.get("compartmentOcid")
if compartment_ocid is None:
    compartment_ocid = tenancy_ocid
allowed_ip_address = config.get_secret_object("oci-infra:allowedIpAddress")
if allowed_ip_address is None:
    allowed_ip_address = ["0.0.0.0/0"]

ad = oci.identity.get_availability_domain_output(
    compartment_id=tenancy_ocid, ad_number=1
)

vcn = oci.core.VirtualNetwork(
    "vcn",
    cidr_block="10.1.0.0/16",
    compartment_id=compartment_ocid,
    display_name="vcn-ussanjose-1",
    dns_label="VcnUSSJC1",
)

internet_gateway = oci.core.InternetGateway(
    "internet_gateway",
    compartment_id=compartment_ocid,
    display_name="vcn-ig",
    vcn_id=vcn.id,
)

route_table = oci.core.RouteTable(
    "route_table",
    compartment_id=compartment_ocid,
    vcn_id=vcn.id,
    display_name="vcn-routetable",
    route_rules=[
        {
            "destination": "0.0.0.0/0",
            "destination_type": "CIDR_BLOCK",
            "network_entity_id": internet_gateway.id,
        }
    ],
)

public_security_list = oci.core.SecurityList(
    "public_security_list",
    ingress_security_rules=[
        {
            "protocol": "6",
            "source": ip,
            "tcp_options": {
                "max": 443,
                "min": 443,
            },
        }
        for ip in allowed_ip_address
    ],
    compartment_id=compartment_ocid,
    vcn_id=vcn.id,
    display_name="public-vcn-security-list",
    egress_security_rules=[
        {
            "protocol": "6",
            "destination": "0.0.0.0/0",
        }
    ],
)

public_subnet = oci.core.Subnet(
    "public_subnet",
    cidr_block="10.1.10.0/24",
    display_name="public-subnet",
    dns_label="PublicSubnet",
    security_list_ids=[public_security_list.id],
    compartment_id=compartment_ocid,
    vcn_id=vcn.id,
    route_table_id=route_table.id,
    dhcp_options_id=vcn.default_dhcp_options_id,
)

private_security_list = oci.core.SecurityList(
    "private_security_list",
    compartment_id=compartment_ocid,
    vcn_id=vcn.id,
    display_name="private-vcn-security-list",
    egress_security_rules=[
        {
            "protocol": "6",
            "destination": "0.0.0.0/0",
        }
    ],
    ingress_security_rules=[
        {
            "protocol": "6",
            "source": "10.1.0.0/16",
        }
    ],
)

private_subnet = oci.core.Subnet(
    "private_subnet",
    cidr_block="10.1.20.0/24",
    display_name="private-subnet",
    dns_label="PrivateSubnet",
    security_list_ids=[private_security_list.id],
    compartment_id=compartment_ocid,
    vcn_id=vcn.id,
    route_table_id=route_table.id,
    dhcp_options_id=vcn.default_dhcp_options_id,
)

# Outputs
pulumi.export("vcn_id", vcn.id)
pulumi.export("private_subnet_id", private_subnet.id)
pulumi.export("public_subnet_id", public_subnet.id)
pulumi.export("internet_gateway_id", internet_gateway.id)
