import os
import time
from datetime import datetime
from aws_vps_manager_backend.instance import Instance


class InstanceManager:
    """The instance manager
    """

    _class_instance = None

    def __init__(self):
        self._instance = Instance()
        self._shared_dir_path = "/mnt/avm_shared"

    def __new__(cls, *args, **kwargs):
        if not cls._class_instance:
            cls._class_instance = super(InstanceManager, cls).__new__(cls)
        return cls._class_instance
  
    @property
    def instance(self) -> Instance:
        """The instance object
        """
        return self._instance

    @property
    def shared_dir_path(self) -> os.path:
        """The path of the shared directory used to store exchange files with the frontend
        """
        return self._shared_dir_path
  
    @shared_dir_path.setter
    def shared_dir_path(self, value: os.path):
        self._shared_dir_path = value

    def set_state(self, state: str):
        """Set the set of the instance for the frontend

        Args:
            state (str): The state of the instance
        """
        with open(f"{self._shared_dir_path}/state", "w", encoding="utf-8") as state_file:
            state_file.write(state)

    def run(self):
        """The runner loop
        """
        while True:
            state = self.instance.get_state()
            if state is None :
                state = 'unknown'
            self.set_state(state)

            if state == "running":
                public_ip = self._instance.get_ip()
                if public_ip:
                    with open(f"{self._shared_dir_path}/ip_address", "w", encoding="utf-8") as ip_address_file:
                        ip_address_file.write(public_ip)

            if os.path.isfile(f"{self._shared_dir_path}/spinup_requested"):
                print("A system spinup has been requested")
                if state in ['down', 'error', 'unknown']:
                    print("The instance does not exist : proceeding to instance creation")
                    self.set_state('spinning-up')
                    if self.instance.spinup():
                        self.set_state('running')
                    else:
                        self.set_state('error')
                os.remove(f"{self._shared_dir_path}/spinup_requested")

            if os.path.isfile(f"{self._shared_dir_path}/spindown_scheduled"):
                scheduled_shutdown_time_str = '2050-12-31 00:00:00'
                with open(f"{self._shared_dir_path}/spindown_scheduled", "r", encoding="utf-8") as shutdown_scheduled_file:
                    scheduled_shutdown_time_str = shutdown_scheduled_file.readline().strip()
                scheduled_shutdown_time = datetime.strptime(scheduled_shutdown_time_str, '%Y-%m-%d %H:%M:%S')
                current_time = datetime.now()
                if current_time >= scheduled_shutdown_time:
                  
                    print("A system spindown schedule has been missed : spinning-down.")
                    self.set_state('spinning-down')
                    os.remove(f"{self._shared_dir_path}/spindown_scheduled")
                    if self.instance.spindown():
                        self.set_state('down')
                    else:
                        self.set_state('error')

            time.sleep(15)
