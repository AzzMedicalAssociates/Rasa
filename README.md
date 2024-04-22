# Rasa
Deploying Rasa Chatbot on Hostinger VPS Server
This guide will help you deploy a Rasa chatbot on a Hostinger VPS server using Docker containers for both the Rasa chatbot and the custom action server.

Prerequisites
Before you begin, make sure you have the following:

Hostinger VPS server with Docker installed
Docker-compose installed on your local machine
Steps
1. Dockerfiles
Create two Dockerfiles, one for the Rasa chatbot and one for the custom action server. These Dockerfiles will define the environment for each component.

2. Copy Files
In the Dockerfile for the action server, copy all the necessary files into the container, just like you would in the Dockerfile for the Rasa chatbot.

3. Download Chrome and ChromeDriver
In the Dockerfile for the action server, download Google Chrome Stable using the curl command. Additionally, manually download the corresponding version of ChromeDriver from the official website and copy it into the container. Ensure you provide executable permission to the ChromeDriver.

4. Configure Endpoints
In the endpoints.yml file of your Rasa project, add the action endpoint for the custom action server. Replace the URL with the URL of the running action server container and the port with the container port.
