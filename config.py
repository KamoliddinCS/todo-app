import os
import dotenv

dotenv.load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")