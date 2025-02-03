import os
class KodeConfig:
    @staticmethod
    def get(key):
        config = {
            "db_name": os.getenv("DB_NAME"),
            "db_user": os.getenv("DB_USER"),
            "db_password": os.getenv("DB_PASSWORD"),
            "db_port": os.getenv("DB_PORT"),
            "shared_data_path": os.getenv("SHARED_DATA_PATH")
        }

        return config.get(key)