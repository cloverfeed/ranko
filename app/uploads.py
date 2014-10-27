from flask.ext.uploads import UploadSet
import os.path

def documents_dir(app):
    return os.path.join(app.instance_path, 'uploads')


documents = UploadSet('documents',
                      extensions=['pdf'],
                      default_dest=documents_dir,
                      )
