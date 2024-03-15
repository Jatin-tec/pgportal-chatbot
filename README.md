# Real-Time Chatbot Flask App

This project is a Flask-based real-time chatbot application capable of switching between rule-based responses and language model (LLM) generated responses as needed. Configuration is managed through JSON files. The entire application, including all databases, is dockerized for easy setup and deployment.

## Screenshots

Here are some screenshots of the chatbot in action:

![Chatbot Interface](/assets/features.png)

![Chatbot Conversation](/assets/chat1.png "Chatbot Conversation")


## Features

- Real-time chat functionality.
- Switch between rule-based and LLM dynamically.
- Dockerized environment for easy setup.
- JSON-based configuration.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Docker and Docker Compose installed on your system.
- Python 3.x installed on your system (replace with your specific Python version requirement).

## Setup and Installation

1.  **Clone the Repository**

    ```bash
    git clone git@github.com:Jatin-tec/pgportal-chatbot.git
    
    cd pgportal-chatbot
    ```

2.  **Create a Virtual Environment**

    It's recommended to create a Python virtual environment to manage dependencies.
    
    ```bash
    python3 -m venv venv
    
    source venv/bin/activate 
    ```

3. **Install Requirements**

    Install the Python dependencies required for the project.

    ```bash 
    pip install -r requirements.txt
    ```

4. **Docker Compose**

    Use Docker Compose to build and run the containers for the application and databases

    ```bash 
    docker-compose up --build
    ```
    This command builds the images if they don't exist and starts the containers. To run the containers in the background, add the -d flag.

5. **Populate the Database**

    After the containers are up and running, execute the scripts to populate the 
    database with the necessary initial data.

    ```bash 
    bash setup.sh
    ```
