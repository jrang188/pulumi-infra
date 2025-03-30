import pulumi
import pulumi_oci as oci


class ComputeInstance:
    def __init__(
        self,
        oci_config: pulumi.Config,
        config: pulumi.Config,
        instance_name: str,
        instance_ocpus: int,
        instance_memory_in_gbs: int,
        subnet_id: id,
        amd64_cpu: bool = False,
    ):
        # -----------------------------------------------------------
        # Configuration
        # -----------------------------------------------------------
        self.instance_name = instance_name
        self.tenancy_ocid = oci_config.require("tenancyOcid")
        self.compartment_ocid = oci_config.get("compartmentOcid") or self.tenancy_ocid
        self.availability_domains = oci.identity.get_availability_domains(
            self.compartment_ocid
        )
        self.public_ssh_key = config.get("sshPublicKey")
        self.instance_shape = (
            "VM.Standard.A1.Flex" if not amd64_cpu else "VM.Standard.E2.1.Micro"
        )
        self.image_ocid = (
            "ocid1.image.oc1.us-sanjose-1.aaaaaaaafy4nk2hjdtesoq6cpgfatvxjuq7jbz5dbezoar7hdynf7m2kwfjq"  # Canonical-Ubuntu-24.04-Minimal-aarch64-2025.01.31-1
            if not amd64_cpu
            else "ocid1.image.oc1.us-sanjose-1.aaaaaaaanvsql7upvg6klgd7c35sfx4du5oqp73sxpvtufldwpxatfgeonhq"  # Canonical-Ubuntu-24.04-Minimal-2025.01.31-1
        )  # Replace with your image OCID.
        self.instance_ocpus = instance_ocpus
        self.instance_memory_in_gbs = instance_memory_in_gbs
        self.subnet_id = subnet_id

        # -----------------------------------------------------------
        # Create Resources
        # -----------------------------------------------------------
        self._create_vm()

    def _create_vm(self):
        self.instance = oci.core.Instance(
            self.instance_name,
            availability_domain=self.availability_domains.availability_domains[0].name,
            # Replace with your compartment ID.
            compartment_id=self.compartment_ocid,
            # Using VM.Standard.A1.Flex (ARM) or VM.Standard.E2.1.Micro shape in Always Free Tier
            shape=self.instance_shape,
            # Replace with your subnet ID.
            create_vnic_details=oci.core.InstanceCreateVnicDetailsArgs(
                assign_private_dns_record=True,
                assign_public_ip="true",
                display_name=f"vnic-{self.instance_name}",
                subnet_id=self.subnet_id,
            ),
            # Metadata for the instance, including SSH keys for access.
            metadata={"ssh_authorized_keys": self.public_ssh_key},
            # Use an Oracle-provided image or your own custom image.
            source_details=oci.core.InstanceSourceDetailsArgs(
                source_type="image",
                source_id=self.image_ocid,
            ),
            # Specifying the OCPU and memory configurations.
            shape_config=oci.core.InstanceShapeConfigArgs(
                ocpus=self.instance_ocpus,  # Number of OCPUs.
                memory_in_gbs=self.instance_memory_in_gbs,  # Amount of RAM in GBs.
            ),
            # Additional arguments like display name, can be specified here.
            display_name=self.instance_name,
        )

    def output(self):
        pulumi.export("instance_name", self.instance.display_name)
        pulumi.export("instance_id", self.instance.id)
        pulumi.export("instance_public_ip", self.instance.public_ip)
        pulumi.export("instance_private_ip", self.instance.private_ip)
