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

4. **Managing the database:**
When you first run the project you might find some warnings about migrations. This means that the database was created but the tables might be missing. Just to be sure run:
    ```sh
    python manage.py makemigrations login presentation
    python manage.py makemigrations presentation
    python manage.py migrate
    ```

5. **Running the project code:**
This part is simple. Just run the following commands (make sure you do previous step first):
    ```sh
    python manage.py runserver
    ```

You can now open the project on any browser.

## Testing (SQLite quick configuration)
For testing purposes, just run the following line:
```
python manage.py test
```
If you somehow need to test a particular module, just type the module
```
python manage.py test [module]
```
Modules available so far are *login* and *presentation*.

This will create a SQLite instance that sets up a test database for you. All test data (files/directories created) will be destroyed as soon as the test finishes.