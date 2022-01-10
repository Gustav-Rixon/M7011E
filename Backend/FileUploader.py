import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from Lorax import upload_user_pic

UPLOAD_FOLDER = 'Database/ProfilePictures/users'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

# TODO convert to Werkzeug if times allows


def allowed_file(filename):
    """[summary]
        Dictates what file formats are allowed to upload
    Args:
        filename ([String]): [The name of the file]

    Returns:
        [Boolean]: [True if allowd, False of file format not in ALLOWED_EXTENSIONS]
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    """[summary]
        This route recives an file from an form typ file and uplodes it to the server.

    Returns:
        [redirect]: [redirects user after successfully a upload, returns error if not successfully]
    """
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(
                app.config['UPLOAD_FOLDER'], request.form.get('userid')+filename))
            # TODO INSERT FILE PATHE INTO USER TABLE
            upload_user_pic(request.form.get('userid') +
                            filename, request.form.get('userid'))
            return redirect(url_for('uploader',
                                    filename=filename))  # TODO REDERACT TO REACTE SITE
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=String name=userid>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
    app.run(debug=True)
