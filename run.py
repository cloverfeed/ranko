from app.factory import create_app


def main():
    app = create_app(db_backend='sql_file')
    app.run(debug=True)

if __name__ == '__main__':
    main()
