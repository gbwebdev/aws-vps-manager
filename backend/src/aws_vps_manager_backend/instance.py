import time 

from aws_vps_manager_backend.aws_api_client import AwsApiClient

class Instance:
    """LightSail VM instance
    """

    def __init__(self):
        self._client = AwsApiClient().client

        self._name = "default-instance"
        self._blueprint_id = "ubuntu_22_04"
        self._availability_zone = "eu-west-3a"
        self._bundle_id = "small_3_0"
        self._data_disk_name = None
        self._data_disk_path = "/dev/xvdf"
        self._source_snapshot_name = None

        self._status = None


    @property
    def name(self) -> str:
        """Instance name
        """
        return self._name

    @name.setter
    def name(self, value : str):
        self._name = value

    @property
    def blueprint_id(self) -> str:
        """Instance blueprint id
        """
        return self._blueprint_id

    @blueprint_id.setter
    def blueprint_id(self, value : str):
        self._blueprint_id = value

    @property
    def availability_zone(self) -> str:
        """Instance availability zone
        """
        return self._availability_zone

    @availability_zone.setter
    def availability_zone(self, value : str):
        self._availability_zone = value

    @property
    def bundle_id(self) -> str:
        """Instance bundle id
        """
        return self._bundle_id

    @bundle_id.setter
    def bundle_id(self, value : str):
        self._bundle_id = value

    @property
    def data_disk_name(self) -> str:
        """Instance data disk name
        """
        return self._data_disk_name

    @data_disk_name.setter
    def data_disk_name(self, value : str):
        self._data_disk_name = value

    @property
    def data_disk_path(self) -> str:
        """Instance data disk path (mountpoint)
        """
        return self._data_disk_path

    @data_disk_path.setter
    def data_disk_path(self, value : str):
        self._data_disk_path = value


    @property
    def source_snapshot_name(self) -> str:
        """Source instance snapshot
        """
        return self._source_snapshot_name

    @source_snapshot_name.setter
    def source_snapshot_name(self, value : str):
        self._source_snapshot_name = value



    def _create_instance(self):
        """Create a new instance from the snapshot
        """
        try:
            response = self._client.create_instances_from_snapshot(
                instanceNames=[self._name],
                availabilityZone=self._availability_zone,
                # blueprintId=self._blueprint_id,
                bundleId=self._bundle_id,
                instanceSnapshotName = self._source_snapshot_name,
                attachedDiskMapping={
                    'home': [
                        {
                            'originalDiskPath': 'string',
                            'newDiskName': 'string'
                        },
                    ]
                },
                # userData=f"""#cloud-config
                # mounts:
                # - [ {self._data_disk_path}, /home, ext4, "defaults,nofail", 0, 2 ]
                # """
            )
            print("Instance creation initiated:", response)
        except Exception as e:
            print("Error creating instance:", e)
            return False
        return True

    # def _attach_disk(self):
    #     try:
    #         response = self._client.attach_disk(
    #             diskName=self._data_disk_name,
    #             instanceName=self._name,
    #             diskPath=self._data_disk_path
    #         )
    #         print("Disk attachment initiated:", response)
    #     except Exception as e:
    #         print("Error attaching disk:", e)
    #         return False
    #     return True

    # def _detach_disk(self):
    #     try:
    #         response = self._client.detach_disk(
    #             diskName=self._data_disk_name
    #         )
    #         print("Disk detachment initiated:", response)
    #     except Exception as e:
    #         print("Error detaching disk:", e)
    #         return False
    #     return True

    def _shutdown_instance(self):
        """Shutdown the instance
        """
        try:
            response = self._client.stop_instance(
                instanceName=self._name
            )
            print("Instance shutdown initiated:", response)
        except Exception as e:
            print("Error shutting down instance", e)
            return False
        return True

    def _wait_for_instace_to_be_shutdown(self):
        """Wait for the instance to be down
        """
        while self.get_state() != "stopped":
            print(self.get_state())
            time.sleep(5)

    def _create_snapshot(self):
        """Create a snapshot of the instance
        """
        try:
            response = self._client.create_instance_snapshot(
                instanceName = self._name,
                instanceSnapshotName=self.source_snapshot_name
            )
            print("Instance snapshot creation initiated:", response)
        except Exception as e:
            print("Error creating instance snapshot", e)

    def _delete_snapshot(self):
        """Delete the snapshot
        """
        try:
            response = self._client.delete_instance_snapshot(
                instanceSnapshotName=self.source_snapshot_name
            )
            print("Instance snapshot deletion initiated:", response)
        except Exception as e:
            print("Error deleting instance snapshot", e)
            return False
        
        return True

    def _delete_instance(self):
        """Delete the instance
        """
        try:
            response = self._client.delete_instance(
                instanceName=self._name
            )
            print("Instance deletion initiated:", response)
        except Exception as e:
            print("Error deleting instance:", e)
            return False
        
        return True
    
    def _wait_for_instace_snapshot_to_be_ready(self):
        """Wait for the instance to be ready
        """
        print("Wainting for instance snapshot to be ready")
        while self.get_instance_snapshot_state() != "available":
            print(self.get_instance_snapshot_state())
            time.sleep(5)

    def _wait_for_instace_snapshot_to_be_deleted(self):
        """Wait for the instance to be deleted
        """
        print("Wainting for instance snapshot to be deleted")
        while self.get_instance_snapshot_state() != "notFound":
            print(self.get_instance_snapshot_state())
            time.sleep(5)

    def spinup(self):
        """Spinup the instance
        """
        self._create_instance()
        # self._attach_disk()
        
        return True

    def spindown(self):
        """Spindown the instance
        """

        self._shutdown_instance()
        self._wait_for_instace_to_be_shutdown()
        time.sleep(1)
        # self._detach_disk()
        self._delete_snapshot()
        self._wait_for_instace_snapshot_to_be_deleted()
        time.sleep(1)
        self._create_snapshot()
        self._wait_for_instace_snapshot_to_be_ready()
        time.sleep(5)
        self._delete_instance()

        return True

    def get_ip(self) -> str:
        """Get the IP of the instance

        Returns:
            str: The instance IP address
        """
        try:
            response = self._client.get_instance(instanceName=self._name)
            public_ip = response['instance']['publicIpAddress']
            return public_ip
        except AwsApiClient().client.exceptions.NotFoundException as e:
            pass
        except Exception as e:
            print(f"Error retrieving instance public IP: {e}")
            return None

    def get_state(self) -> str:
        """Get the instance state

        Returns:
            str: The instance state
        """
        try:
            response = self._client.get_instance(instanceName=self._name)
            state = response['instance']['state']['name']
            return state
        except AwsApiClient().client.exceptions.NotFoundException as e :
            return "down"
        except Exception as e:
            print(f"Error retrieving instance state: {e}")
            return None

    def get_instance_snapshot_state(self) -> str:
        """Get the snapshot state

        Returns:
            str: The snapshot state
        """
        try:
            response = self._client.get_instance_snapshot(instanceSnapshotName =self._source_snapshot_name)
            state = response['instanceSnapshot']['state']
            return state
        except AwsApiClient().client.exceptions.NotFoundException as e :
            return "notFound"
        except Exception as e:
            print(f"Error retrieving instance state: {e}")
            return None
