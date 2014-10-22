import app
import flask.ext.migrate

def main():
    app.db.create_all()
    with app.app.app_context():
        flask.ext.migrate.stamp()

if __name__ == '__main__':
    main()
