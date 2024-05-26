import boto3
import click

from aws_vps_manager_backend.manager import InstanceManager


instance_manager = InstanceManager()


@click.command()
@click.option(
    "--instance-name",
    prompt=True,
)
@click.option(
    "--source-snapshot-name",
    prompt=True,
)
@click.option(
    "--instance-blueprint",
    prompt=True,
    default="ubuntu_22_04",
)
@click.option(
    "--instance-availability-zone",
    prompt=True,
    default="eu-west-3a",
)
@click.option(
    "--instance-bundle-id",
    prompt=True,
    default="small_3_0",
)
@click.option(
    "--instance-data-disk-name",
    prompt=True
)
@click.option(
    "--instance-data-disk-path",
    prompt=True,
    default="/dev/xvdf",
)
@click.option(
    "--shared-dir-path",
    type=click.Path(exists=True),
    default="/mnt/avm-shared",
)
def entrypoint(instance_name,
               source_snapshot_name,
               instance_blueprint,
               instance_availability_zone,
               instance_bundle_id,
               instance_data_disk_name,
               instance_data_disk_path,
               shared_dir_path):

    instance_manager.instance.name = instance_name
    instance_manager.instance.source_snapshot_name = source_snapshot_name
    instance_manager.instance.blueprint_id = instance_blueprint
    instance_manager.instance.availability_zone = instance_availability_zone
    instance_manager.instance.bundle_id = instance_bundle_id
    instance_manager.instance.data_disk_name = instance_data_disk_name
    instance_manager.instance.data_disk_path = instance_data_disk_path
    instance_manager.shared_dir_path = shared_dir_path

    instance_manager.run()


def cli():
    entrypoint(auto_envvar_prefix='AVMB')
