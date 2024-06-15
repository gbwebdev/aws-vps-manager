# Frontend application

This is the frontend for the applications that drives the AWS Lightsail VM instance lifecycle.

It uses files to exchange informations with the backend application.
This may seems like an archaic way of doing things (and in a way it is), but there are two very good reasons to do it like this :
- The requirements are very simples, and I did not want to dive into a unnecessarily complex design.
- It is a very simple way of detaching the component accessible from the Internet (the frontend) and the component that interacts with AWS (the backend).