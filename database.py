import psycopg2
from config import *


class Database:
    __connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name,
    )
    __connection.autocommit = True

    def create_table(self, table_name: str):
        with self.__connection.cursor() as cursor:
            cursor.execute(
                f"""CREATE TABLE IF NOT EXISTS {table_name}(
                    id serial PRIMARY KEY,
                    user_name varchar(100) NOT NULL,
                    current_link varchar(200) NOT NULL
                )"""
            )

    def insert_data(self, table_name: str, fields: list, values: list):
        fields_string = self.__convert_data_list_to_string(fields)
        values_string = self.__convert_data_list_to_string(values, need_string=True)

        with self.__connection.cursor() as cursor:
            cursor.execute(
                f"""INSERT INTO {table_name}({fields_string}) VALUES
                ({values_string});"""
            )

    def select_data(self, table_name: str, field: str, condition=""):
        with self.__connection.cursor() as cursor:
            condition_expression = f"WHERE {condition}" if condition.replace(" ", "") != "" else ""
            cursor.execute(
                f"""SELECT {field} FROM {table_name} {condition_expression};"""
            )

            result = cursor.fetchall()
            return result

    def update_data(self, table_name: str, field: str, new_value, condition=""):
        with self.__connection.cursor() as cursor:
            cursor.execute(
                f"""UPDATE {table_name} SET {field} = '{new_value}' WHERE {condition};"""
            )

    def close_connection(self):
        self.__connection.close()

    @staticmethod
    def __convert_data_list_to_string(array: list, need_string=False):
        string = ""
        for i in array:
            i = str(i)
            if need_string:
                string += "'" + i + "', " if array.index(i) != len(array) - 1 else "'" + i + "'"
            else:
                string += i + ", " if array.index(i) != len(array) - 1 else i
        return string
