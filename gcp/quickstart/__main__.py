"""A Google Cloud Python Pulumi program"""

import pulumi
from pulumi_gcp import storage

# Create a GCP resource (Storage Bucket)
bucket = storage.Bucket(
    "my-bucket",
    location="US",
    website={"main_page_suffix": "index.html"},
    uniform_bucket_level_access=True,
)


bucket_object = storage.BucketObject(
    "index.html", bucket=bucket.name, source=pulumi.FileAsset("index.html")
)

bucket_iam_binding = storage.BucketIAMBinding(
    "my-bucket-binding",
    bucket=bucket.name,
    role="roles/storage.objectViewer",
    members=["allUsers"],
)

pulumi.export(
    "bucket_endpoint",
    pulumi.Output.concat(
        "http://storage.googleapis.com/", bucket.id, "/", bucket_object.name
    ),
)
