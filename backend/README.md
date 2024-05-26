# Backend application

This applications drives the AWS Lightsail VM instance lifecycle.

It uses files to exchange informations with the frontend application.
One could also use the backend without any frontend by simply writing and reading files in the `shared directory` :
- To start the VM, write a file named `spinup_requested` with the content `true`
- To schedule the shutdown, write a file named `spindown_scheduled` with the desired shutdown date and time (`%Y-%m-%d %H:%M:%S`).
