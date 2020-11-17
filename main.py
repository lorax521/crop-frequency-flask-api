if __name__ == "__main__":
    from app import app
    app.config.from_object("app.config.DevConfig")
    app.run()
