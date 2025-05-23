# Event Manager

This repository contains a FastAPI application designed for building robust and scalable web services. It leverages a modern stack of technologies including **Kafka, Zookeeper, Mailhog, MySQL, and Redis**, all orchestrated with **Docker Compose** for easy setup and management.

-----

## Table of Contents

  * [Features](https://www.google.com/search?q=%23features)
  * [Prerequisites](https://www.google.com/search?q=%23prerequisites)
  * [Getting Started](https://www.google.com/search?q=%23getting-started)
      * [Clone the Repository](https://www.google.com/search?q=%23clone-the-repository)
      * [Setup Backend Services with Docker Compose](https://www.google.com/search?q=%23setup-backend-services-with-docker-compose)
      * [Setup Python Environment and Run FastAPI Application](https://www.google.com/search?q=%23setup-python-environment-and-run-fastapi-application)
  * [Project Structure](https://www.google.com/search?q=%23project-structure)
  * [Dependencies](https://www.google.com/search?q=%23dependencies)
  * [Contributing](https://www.google.com/search?q=%23contributing)
  * [License](https://www.google.com/search?q=%23license)

-----

## Features

  * **FastAPI Backend:** A high-performance, asynchronous web framework for building APIs.
  * **Kafka & Zookeeper:** For robust, distributed messaging and event streaming, enabling real-time data processing.
  * **Mailhog:** A lightweight SMTP server for testing email functionality during development without sending actual emails.
  * **MySQL:** A reliable relational database for persistent data storage.
  * **Redis:** An in-memory data store used for caching, session management, and potentially as a broker for asynchronous tasks.
  * **APScheduler:** For asynchronous task processing and cron-like scheduled jobs, ensuring background operations run reliably.
  * **Docker Compose:** Simplifies the setup and management of all backend services with a single command.

-----

## Prerequisites

Before you begin, ensure you have the following installed on your system:

  * **Git:** For cloning the repository.
      * [Download Git](https://git-scm.com/downloads)
  * **Docker Desktop (or Docker Engine + Docker Compose):** Essential for running the backend services.
      * [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
  * **Python 3.8+:** For running the FastAPI application.
      * [Download Python](https://www.python.org/downloads/)

-----

## Getting Started

Follow these steps to get the application up and running on your local machine.

### Clone the Repository

First, clone the project [repository](https://github.com/Aneesh7402/event-manager) to your local machine:



### Setup Backend Services with Docker Compose

This project uses Docker Compose to manage its backend services (Kafka, Zookeeper, Mailhog, MySQL, Redis). You'll find four separate `docker-compose.yml` files (or similarly named `.yml` files for each service group).

1.  **Navigate to your project root** (where your `.yml` files are located).

2.  **Start the services using Docker Compose:**

    ```bash
    docker compose -f kafka.yml up -d
    docker compose -f mailhog.yml up -d
    docker compose -f mysql.yml up -d
    docker compose -f redis.yml up -d
    ```

    *(**Note:** If your project structure uses a single, combined `docker-compose.yml` file for all services, you would simply run `docker compose up -d` in the root directory.)*

    Allow a few moments for all containers to start up and initialize (especially Kafka and MySQL). You can check their status with `docker ps`.

### Setup Python Environment and Run FastAPI Application

1.  **Create a Python Virtual Environment:**
    It's highly recommended to use a virtual environment to manage your project's Python dependencies.

    ```bash
    python -m venv .venv
    ```

2.  **Activate the Virtual Environment:**

      * **On Windows (Command Prompt):**
        ```cmd
        .venv\Scripts\activate.bat
        ```
      * **On Windows (PowerShell):**
        ```powershell
        .venv\Scripts\Activate.ps1
        ```
      * **On macOS/Linux:**
        ```bash
        source .venv/bin/activate
        ```

    You'll know it's active when `(.venv)` appears at the beginning of your terminal prompt.

3.  **Install Python Dependencies:**
    Once your virtual environment is active, install all the required Python packages using the provided `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

    Here's the content of your `requirements.txt` for reference:

    ```
    amqp==5.3.1
    annotated-types==0.7.0
    anyio==4.9.0
    APScheduler==3.11.0
    asyncio==3.4.3
    bcrypt==4.3.0
    billiard==4.2.1
    celery==5.5.2
    cffi==1.17.1
    click==8.2.0
    click-didyoumean==0.3.1
    click-plugins==1.1.1
    click-repl==0.3.0
    colorama==0.4.6
    croniter==6.0.0
    cryptography==45.0.2
    dnspython==2.7.0
    ecdsa==0.19.1
    email_validator==2.2.0
    fastapi==0.115.12
    greenlet==3.2.2
    h11==0.16.0
    idna==3.10
    kafka==1.3.5
    kafka-python==2.2.8
    kombu==5.5.3
    mysql-connector-python==9.3.0
    passlib==1.7.4
    prompt_toolkit==3.0.51
    pyasn1==0.4.8
    pycparser==2.22
    pydantic==2.11.4
    pydantic-settings==2.9.1
    pydantic_core==2.33.2
    pyodbc==5.2.0
    python-dateutil==2.9.0.post0
    python-dotenv==1.1.0
    python-jose==3.4.0
    pytz==2025.2
    redis==6.1.0
    rsa==4.9.1
    six==1.17.0
    sniffio==1.3.1
    SQLAlchemy==2.0.41
    starlette==0.46.2
    typing-inspection==0.4.0
    typing_extensions==4.13.2
    tzdata==2025.2
    tzlocal==5.3.1
    uvicorn==0.34.2
    vine==5.1.0
    wcwidth==0.2.13
    ```

4.  **Run the FastAPI Application:**
    Once all dependencies are installed, you can start your FastAPI application:

    ```bash
    uvicorn app.main:app --reload --port 8000
    ```

      * `app.main:app`: Assumes your main FastAPI application instance is named `app` inside `main.py` within an `app` directory. Adjust this if your structure is different.
      * `--reload`: Enables hot-reloading, so changes to your code will automatically restart the server (great for development).
      * `--port 8000`: Runs the application on port 8000.

    Your application will now be accessible in your browser at `http://127.0.0.1:8000` (or `http://localhost:8000`). The API documentation (Swagger UI) will typically be available at `http://127.0.0.1:8000/docs`.

-----

## Project Structure

(This section is a placeholder. You should fill this in with a brief overview of your project's directory and file structure, e.g.:)

```
my_fastapi_app/
├── app/
│   ├── main.py            # Main FastAPI application
│   ├── api/               # API routes (e.g., v1/)
│   ├── core/              # Configuration, settings, utilities
│   ├── db/                # Database models
│   ├── middleware/        # Middleware for auth
│   ├── repository/        # Database interaction
│   ├── schema/            #DTOs
│   ├── utils/             #utils
│   └── services/          # Business logic, external integrations
├── docker-compose-kafka.yml
├── docker-compose-mailhog.yml
├── docker-compose-mysql.yml
├── docker-compose-redis.yml
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables
└── README.md
```

-----

## Dependencies

This project relies on the following key technologies and Python libraries:

  * **FastAPI**
  * **Uvicorn**
  * **Docker**
  * **Docker Compose**
  * **Apache Kafka**
  * **Apache Zookeeper**
  * **MySQL**
  * **Redis**
  * **Mailhog**
  * **APScheduler** (for cron-like jobs)
  * **SQLAlchemy** (ORM for database interactions)
  * **`mysql-connector-python`** (MySQL driver)
  * **`kafka-python`** (Kafka client)
  * **`redis`** (Redis client)
  * **`python-jose`**, `passlib`, `bcrypt` (for security/authentication)
  * ...and various other supporting libraries listed in `requirements.txt`.


-----

## Implementation Details

For a deeper dive into the architecture, design choices, and specific implementation aspects of this project, please refer to the dedicated [Implementation Details](https://docs.google.com/document/d/1K2AA2OCbdMrWc8hVJ2ltOtizq_9Zxc1ITLMJkbIhXiw/edit?usp=sharing) document.

-----

**Note:** Everything has been made super easy with the Docker files. You don't have to install anything additional on your system other than Docker and Git to get the backend services running! Python is only needed for the FastAPI application itself.


-----

## API Documentation

This FastAPI application comes with built-in interactive API documentation, powered by OpenAPI (formerly Swagger) and ReDoc. Once the application is running, you can explore the available endpoints, test them directly, and understand their schemas.

* **Swagger UI:** Accessible at `http://127.0.0.1:8000/docs`
* **ReDoc:** Accessible at `http://127.0.0.1:8000/redoc`

-----
