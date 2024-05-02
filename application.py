# FileName: application.py
# Description: The main entry point for the web application.
# Author: Petr Štípek
# Date: 2024

from flaskr import create_application

application = create_application()

if __name__ == "__main__":
    application.run(debug=True)
    