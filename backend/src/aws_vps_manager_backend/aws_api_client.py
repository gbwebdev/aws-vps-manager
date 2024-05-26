import boto3

class AwsApiClient:
    """Interface for AWS API
    """
    _class_instance = None
  
    def __init__(self):
        self._client = boto3.client('lightsail')
  
    def __new__(cls, *args, **kwargs):
        if not cls._class_instance:
            cls._class_instance = super(AwsApiClient, cls).__new__(cls)
        return cls._class_instance
    
    @property
    def client(self) -> boto3.client:
        return self._client
