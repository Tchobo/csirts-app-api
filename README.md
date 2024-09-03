# CSIRT API PROJECT

A web api to manage information about CSIRT (Computer Security Incident Response Team) in Africa.

## Table of Contents

- [Project Name](#project-name)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Running the Project Locally](#running-the-project-locally)
  - [Deploying to Render](#deploying-to-render)
  - [Running Tests](#running-tests)
  - [Usage](#usage)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- CRUD about CSIRT
- Filter a CSIRT or list of CSIRT informations. 
- Display all CSIRTs on a map of Africa 

## Prerequisites

Before you start, make sure you have the following tools installed:

- Git
- Docker
- Docker Compose
- A Render account (for deployment)

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/Tchobo/csirts-app-api.git
    cd csirts-app-api
    ```

2. **Build the Docker containers:**

    ```bash
    docker-compose build
    ```

## Environment Variables

Create a `.env` file in the root directory of the project with the following content:

```bash
DEBUG=1
SECRET_KEY=your_secret_key
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASS=your_db_password
DB_HOST=db
DB_PORT=5432

## Running the Project Locally

To run the project locally using Docker and Docker Compose:

1. **Ensure Docker and Docker Compose are installed:**
   - Install Docker: [Docker Installation](https://www.docker.com/products/docker-desktop)
   - Install Docker Compose: [Docker Compose Installation](https://docs.docker.com/compose/install/)

2. **Build the Docker images:**

    ```bash
    docker-compose build
    ```

3. **Start the application and database:**

    ```bash
    docker-compose up
    ```

4. **Apply migrations:**

    ```bash
    docker-compose exec app python manage.py migrate
    ```

5. **Collect static files:**

    ```bash
    docker-compose exec app python manage.py collectstatic --noinput
    ```

6. **Access the application:**

   Navigate to `http://localhost:8000` in your browser.

7. **Run Tests (optional):**

    ```bash
    docker-compose exec app python manage.py test
    ```

8. **Stop the application:**

    ```bash
    docker-compose down
    ```

## Deploying to Render

1. **Push your code to GitHub:**

   Make sure your latest changes are pushed to your GitHub repository.

2. **Create a new Web Service on Render:**
   - Go to the Render dashboard and create a new Web Service.
   - Connect your GitHub repository to Render.

3. **Configure the build and deployment settings:**
   - Set the build command to `docker-compose build`.
   - Set the start command to `docker-compose up`.

4. **Set Environment Variables:**
   - Go to the Render dashboard and configure the environment variables as specified in the [Environment Variables](#environment-variables) section.

5. **Deploy:**
   - Click "Deploy" to start the deployment process.

## Running Tests

To run tests in your local development environment:

```bash
docker-compose exec app python manage.py test
