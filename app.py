from flask import Flask, render_template

app = Flask('Review')

@app.route('/')
def home():
    return render_template('home.html')

def main():
    pass
    app.run(debug=True)

if __name__ == '__main__':
    main()
