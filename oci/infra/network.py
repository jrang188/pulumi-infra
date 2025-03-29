import pulumi
import pulumi_oci as oci


class Network:
    def __init__(self, oci_config: pulumi.Config, config: pulumi.Config):
        # -----------------------------------------------------------
        # Configuration
        # -----------------------------------------------------------

        self.tenancy_ocid = oci_config.require("tenancyOcid")
        self.compartment_ocid = oci_config.get("compartmentOcid") or self.tenancy_ocid

        # Retrieve allowed IP addresses or default to open access
        self.allowed_ip_address = config.get_secret_object(
            "oci-infra:allowedIpAddress"
        ) or ["0.0.0.0/0"]

        # -----------------------------------------------------------
        # Create Resources
        # -----------------------------------------------------------
        self._create_vcn()
        self._create_internet_gateway()
        self._create_route_table()
        self._create_security_lists()
        self._create_subnets()

    def _create_vcn(self):
        self.vcn = oci.core.VirtualNetwork(
            "vcn",
            cidr_block="10.1.0.0/16",
            compartment_id=self.compartment_ocid,
            display_name="vcn-ussanjose-1",
            dns_label="VcnUSSJC1",
        )

    def _create_internet_gateway(self):
        self.internet_gateway = oci.core.InternetGateway(
            "internet_gateway",
            compartment_id=self.compartment_ocid,
            display_name="vcn-ig",
            vcn_id=self.vcn.id,
        )

    def _create_route_table(self):
        self.route_table = oci.core.RouteTable(
            "route_table",
            compartment_id=self.compartment_ocid,
            vcn_id=self.vcn.id,
            display_name="vcn-routetable",
            route_rules=[
                {
                    "destination": "0.0.0.0/0",
                    "destination_type": "CIDR_BLOCK",
                    "network_entity_id": self.internet_gateway.id,
                }
            ],
        )

    def _create_security_lists(self):
        # Public Security List allowing HTTPS ingress from allowed IP addresses
        public_ingress_rules = [
            {
                "protocol": "6",
                "source": ip,
                "tcp_options": {"min": 443, "max": 443},
            }
            for ip in self.allowed_ip_address
        ]

        self.public_security_list = oci.core.SecurityList(
            "public_security_list",
            compartment_id=self.compartment_ocid,
            vcn_id=self.vcn.id,
            display_name="public-vcn-security-list",
            ingress_security_rules=public_ingress_rules,
            egress_security_rules=[{"protocol": "6", "destination": "0.0.0.0/0"}],
        )

        # Private Security List allowing ingress traffic within the VCN CIDR
        self.private_security_list = oci.core.SecurityList(
            "private_security_list",
            compartment_id=self.compartment_ocid,
            vcn_id=self.vcn.id,
            display_name="private-vcn-security-list",
            ingress_security_rules=[{"protocol": "6", "source": "10.1.0.0/16"}],
            egress_security_rules=[{"protocol": "6", "destination": "0.0.0.0/0"}],
        )

    def _create_subnets(self):
        # Public Subnet using public security list and route table
        self.public_subnet = oci.core.Subnet(
            "public_subnet",
            cidr_block="10.1.10.0/24",
            compartment_id=self.compartment_ocid,
            vcn_id=self.vcn.id,
            display_name="public-subnet",
            dns_label="PublicSubnet",
            security_list_ids=[self.public_security_list.id],
            route_table_id=self.route_table.id,
            dhcp_options_id=self.vcn.default_dhcp_options_id,
        )

        # Private Subnet using private security list and same route table
        self.private_subnet = oci.core.Subnet(
            "private_subnet",
            cidr_block="10.1.20.0/24",
            compartment_id=self.compartment_ocid,
            vcn_id=self.vcn.id,
            display_name="private-subnet",
            dns_label="PrivateSubnet",
            security_list_ids=[self.private_security_list.id],
            route_table_id=self.route_table.id,
            dhcp_options_id=self.vcn.default_dhcp_options_id,
        )
