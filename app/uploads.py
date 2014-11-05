import os.path

from flask.ext.uploads import UploadSet


def documents_dir(app):
    return os.path.join(app.instance_path, 'uploads')


documents = UploadSet('documents',
                      extensions=['pdf', 'png'],
                      default_dest=documents_dir,
                      )
