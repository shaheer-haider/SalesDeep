import os
import pymysql
from dotenv import load_dotenv

def get_db_connection():
    """
    Establishes and returns a database connection using pymysql.
    """
    try:
        load_dotenv()  # Load environment variables from .env file
        host = os.environ.get('DB_HOST')
        user = os.environ.get('DB_USER')
        password = os.environ.get('DB_PASSWORD')
        database = os.environ.get('DB_NAME')
        port = int(os.environ.get('DB_PORT'))

        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            cursorclass=pymysql.cursors.DictCursor  # Ensures results are returned as dictionaries
        )
        return connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def get_data_from_db(table_name):
    """
    Fetches all records from a specified table and returns them as a list of dictionaries.
    Closes the database connection automatically.
    """
    connection = get_db_connection()
    if connection is None:
        print("Invalid database connection.")
        return []

    try:
        with connection.cursor() as cursor:
            query = f"SELECT * FROM {table_name};"
            cursor.execute(query)
            result = cursor.fetchall()  # Fetch all rows as list of dictionaries
        return result
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []
    finally:
        connection.close()  # Close the connection automatically

def insert_data_into_db(db_connection, table_name, data, chunk_size=1000):
    """
    Inserts a list of dictionaries into a specified table with support for "ON DUPLICATE KEY UPDATE".
    """
    if db_connection is None:
        db_connection = get_db_connection()

    if db_connection is None:
        print("Invalid database connection.")
        return

    # Ensure that all dictionaries have the same keys
    columns = data[0].keys()

    # Prepare the values to be inserted, ensuring proper handling of lists of dictionaries
    values = [tuple(d.get(col) for col in columns) for d in data]

    # Prepare the query with placeholders for columns and values
    placeholders = ', '.join(['%s'] * len(columns))
    column_names = ', '.join(columns)

    update_columns = ', '.join([f"{col} = VALUES({col})" for col in columns])
    query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_columns}"

    # Insert the data in chunks to avoid overwhelming the database
    try:
        with db_connection.cursor() as cursor:
            for i in range(0, len(values), chunk_size):
                chunk = values[i:i + chunk_size]
                cursor.executemany(query, chunk)  # Execute the query for each chunk
                db_connection.commit()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        db_connection.close()



# # main function
# if __name__ == "__main__":
#     users = get_data_from_db('users')  # Table name should be 'users' as per your update
#     print(f"Users: {users}")

#     sample_data = [
#         {"user_uid": 173736839589664, "nickname": "Ali", "user_mail": "ali@example.com", "token": "xyz789", "expires_in": 604800, "user_type": 1, "isSuperAdmin": 0, 'company_id': 341, 'company_name': "Ali", 'user_group_id': 234324, 'UserGroupName':'sad', 'country_name': 'adad', 'department_name':'afdsaf'},
#         {"user_uid": 173736839589665, "nickname": "Ahmed", "user_mail": "ahmed@example.com", "token": "xyz790", "expires_in": 604800, "user_type": 1, "isSuperAdmin": 0, 'company_id': 342, 'company_name': "Ahmed Corp", 'user_group_id': 234325, 'UserGroupName':'manager', 'country_name': 'Pakistan', 'department_name':'HR'},
#         {"user_uid": 17368395896633, "nickname": "Sarah", "user_mail": "sarah@example.com", "token": "xyz791", "expires_in": 604800, "user_type": 2, "isSuperAdmin": 0, 'company_id': 343, 'company_name': "Sarah Ltd", 'user_group_id': 234326, 'UserGroupName':'admin', 'country_name': 'USA', 'department_name':'Marketing'},
#         {"user_uid": 1737368395896642, "nickname": "John", "user_mail": "john@example.com", "token": "xyz792", "expires_in": 604800, "user_type": 1, "isSuperAdmin": 0, 'company_id': 344, 'company_name': "John's Co", 'user_group_id': 234327, 'UserGroupName':'dev', 'country_name': 'Canada', 'department_name':'Development'},
#         {"user_uid": 17368395896612, "nickname": "Mira", "user_mail": "mira@example.com", "token": "xyz793", "expires_in": 604800, "user_type": 1, "isSuperAdmin": 0, 'company_id': 345, 'company_name': "Mira Technologies", 'user_group_id': 234328, 'UserGroupName':'ops', 'country_name': 'UK', 'department_name':'Operations'}
#     ]

#     insert_data_into_db("users", sample_data, chunk_size=2000)
