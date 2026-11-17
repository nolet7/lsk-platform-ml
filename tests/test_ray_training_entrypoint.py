import pytest
from examples.ray_training.lsk_training.entrypoint import dataset_location

def test_tenant_scoped_dataset():
    assert dataset_location("s3://approved/tenant-a/datasets/v1.csv","tenant-a","approved")==(
        "approved","tenant-a/datasets/v1.csv")
    with pytest.raises(ValueError):
        dataset_location("s3://approved/other/datasets/v1.csv","tenant-a","approved")
    with pytest.raises(ValueError):
        dataset_location("s3://approved/tenant-a/datasets/../secret","tenant-a","approved")
    with pytest.raises(ValueError):
        dataset_location("https://example.com/file.csv","tenant-a","approved")
