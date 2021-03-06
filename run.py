from app.factory import create_app


def main():
    app = create_app(config_file='conf/development.py')
    app.run(debug=True)

if __name__ == '__main__':
    main()
