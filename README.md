# AWS VPS Manager

This is a toolkit to create, and then manage an Amazon AWS Lightsail VM.

## Ansible

A role and a playbook are provided to handle the VPS setup

## Backend

The backup handles the VPS lifecycle.

It uses files to exchange informations with the frontend application.
One could also use the backend without any frontend by simply writing and reading files in the `shared directory` :
- To start the VM, write a file named `spinup_requested` with the content `true`
- To schedule the shutdown, write a file named `spindown_scheduled` with the desired shutdown date and time (`%Y-%m-%d %H:%M:%S`).
You can gather information on the VM using files also :
- The file `state` contains the state of the VPS.
- The file `ip_address` contains the IP address of the VM.

This may seems like an archaic way of doing things (and in a way it is), but there are two very good reasons to do it this way :
- The requirements are very simples, and I did not want to dive into a unnecessarily complex design.
- It is a very simple way of detaching the component accessible from the Internet (the frontend) and the component that interacts with AWS (the backend).

## Frontend

A simple Flask application that can be used to do drive the backend.

You have to be a registered user to access it.
In case of a wrong password, you must wait one minute to try to authenticate again.
