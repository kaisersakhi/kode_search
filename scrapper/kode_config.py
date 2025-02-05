import os
class KodeConfig:
    @staticmethod
    def get(key):
        config = {
            "db_name": os.getenv("DB_NAME"),
            "db_user": os.getenv("DB_USER"),
            "db_password": os.getenv("DB_PASSWORD"),
            "db_url": os.getenv("DB_URL"),
            "db_port": os.getenv("DB_PORT"),
            "shared_data_path": "/data"
        }

        return config.get(key)