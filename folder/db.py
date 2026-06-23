import boto3
from os import getenv
from datetime import datetime, timezone


class DataBase:
    def __init__(self, table_name: str = "TestTable"):
        self.dynamodb = boto3.resource(
            "dynamodb",
            region_name=getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=getenv("AWS_SECRET_ACCESS_KEY"),
        )
        self.table = self.dynamodb.Table(table_name)

    def __str__(self):
        return str(self.table)

    def add_user(self, user_id: int, full_name: str = ""):
        self.table.put_item(Item={
            "id": user_id,                                          # Number (partition key)
            "created_at": datetime.now(timezone.utc).isoformat(),  # String
            "full_name": full_name,
        })

    def get_user(self, user_id: int):
        response = self.table.get_item(Key={"id": user_id})
        return response.get("Item")

    def get_all_users(self):
        response = self.table.scan()
        return response.get("Items", [])