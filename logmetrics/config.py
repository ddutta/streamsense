import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

CSRF_ENABLED = False
# Secret key for session management. You can generate random strings here:
# http://clsc.net/tools-old/random-string-generator.php
SECRET_KEY = 'my precious'

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')

# file upload folder
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
ALLOWED_EXTENSIONS = set(['txt', 'log', 'sh'])
LAST_FILENAME = None
NUMHASHBITS = 14
PROPAGATE_EXCEPTIONS = True

# elasticsearch
ES_END_PT = "localhost:9200"
