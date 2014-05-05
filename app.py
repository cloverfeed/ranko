from flask import Flask, render_template, flash, redirect, url_for
from flask.ext.wtf import Form
from flask_wtf.file import FileField
import os
from key import get_secret_key

app = Flask('Review')
key_file = os.path.join(app.instance_path, 'secret.key')
app.config['SECRET_KEY'] = get_secret_key(key_file)


@app.route('/')
def home():
    return render_template('home.html')

class UploadForm(Form):
    file = FileField('The file to review')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        flash('Uploaded')
        return redirect(url_for('home'))
    return render_template('upload.html', form=form)

def main():
    pass
    app.run(debug=True)

if __name__ == '__main__':
    main()
