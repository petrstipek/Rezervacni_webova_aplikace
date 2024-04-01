from flaskr import create_application

application = create_application()

if __name__ == "__main__":
    application.run(debug=True)
    