## Installation

To set up the development environment for this project, follow these steps:

1. **Create and activate a virtual environment (recommended):**
    ```sh
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

2. **Clone the repository:**
    ```sh
    git clone https://github.com/LeoEras/ENGI-9839
    cd <project-directory>
    ```

3. **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4. **Configure the database:**
This project works with Postgresql 17, so be sure to [download](https://www.postgresql.org/download/) the requiered files for a complet experience. You might also want to install [PgAdmin](https://www.pgadmin.org/download/pgadmin-4-windows/) to have a GUI interface to the database.
    Edit the database configs on presApp\settings.py file:
    ```py
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            "OPTIONS": {
                "service": "presentationApp",
            },
        }
    }
    ```
    The **service** option should point to the first line present on the ".pg_service.conf" file, which should be visible to the terminal/cmd (this path should be set as an environment variable). The contents and location of the ".pg_service.conf" will vary between Windows and macOS/Linux, so refer to the [documentation](https://www.postgresql.org/docs/current/libpq-pgservice.html).

    The contents of my *.pg_service.conf* file:
    ```sh
    [presentationApp]
    host=localhost
    port=5432
    user=postgres
    dbname=presentationApp
    ```
    You might also need to configure the ".pgpass.conf" file. It follows a similar configuration as last file.
    ```sh
    localhost:5432:presentationApp:postgres:<my_secure_password>
    ```