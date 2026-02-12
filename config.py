import os
import tempfile


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32).hex()
    BASE_DIR = os.path.dirname(__file__)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    ALLOWED_EXTENSIONS = {".csv", ".xls", ".xlsx"}
    DATABASE = os.path.join(BASE_DIR, "data.db")
    TEMPLATE_PATH = os.path.join(BASE_DIR, "template.csv")


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False

    def __init__(self):
        self._db_fd, self.DATABASE = tempfile.mkstemp(suffix=".db")
        self._upload_dir = tempfile.mkdtemp()
        self.UPLOAD_FOLDER = self._upload_dir
