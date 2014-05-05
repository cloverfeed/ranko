from flask import Flask

app = Flask('Review')

@app.route('/')
def home():
    return 'hello'

def main():
    pass
    app.run(debug=True)

if __name__ == '__main__':
    main()
