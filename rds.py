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
#     db_connection = get_db_connection()
#     # users = get_data_from_db('users')  # Table name should be 'users' as per your update
#     # print(f"Users: {users}")

#     sample_data = [
#         {'product_id': 13216337, 'product_name': '3M734 series P120 water sandpaper for car beauty polishing, sanding leather, water sandpaper, dry and wet', 'model': 'P120', 'brand_name': '3M', 'type': 'Industrial Grinding / Grinding sandpaper', 'length': '280mm', 'width': '230mm', 'height': 'mm', 'size': '280mm,230mm,mm', 'weight': '10g', '`leading`': 'In Stock', '`condition`': 'New Sealed Under Guarantee', 'imgs': "['https://cbu01.alicdn.com/img/ibank/O1CN01j948dU1JZHRpJPomf_!!2213299601042-0-cib.jpg']", 'image_url': 'https://cbu01.alicdn.com/img/ibank/O1CN01j948dU1JZHRpJPomf_!!2213299601042-0-cib.jpg', 'price_str': '$0.75 (1-9) $0.74 (10-99) $0.73 (100-199) $0.71 (≥200)', 'description_name': 'P120', 'description_content': 'Product Name: Sandpaper<br/><br>Granularity: P120<br/><br>Abrasive: High quality alumina<br/><br>Usage: dry mill/water mill<br/><br>Specification: 50 sheets per book<br/><br>Product features: Sharp grinding, precise polishing<br/><br>Product Usage: 1. Used for polishing mechanical equipment such as automobiles, ship hulls, and machine tools, as well as polishing precision instruments<br/><br>Light. 2. Used for various alloy products, stainless steel products, non-ferrous metals, black gold<br/><br>Processing and polishing of metal components such as plates and impeller blades. 3. Used for high-end homes<br/><br>Painting and polishing of furniture and wooden products, as well as precision grinding and polishing of jewelry, handicrafts, rattan products, etc.<br/><br>4. Used for polishing oil paint surfaces such as piano instruments and atomic ash, and can be used on jade artifacts<br/><br>Jewelry, jewelry, steel pipes, plastic shells, etc.<br/><br>Product size: 230 * 280mm'},
#         {'product_id': 1731381173202810403, 'product_name': '14', 'model': 'T605F14', 'brand_name': '3M', 'type': 'Accessories', 'length': 'cm', 'width': 'cm', 'height': 'cm', 'size': 'cm,cm,cm', 'weight': 'kg', '`leading`': 'In Stock', '`condition`': 'New Sealed Under Guarantee', 'imgs': "[]", 'image_url': '', 'price_str': '', 'description_name': 'T605F', 'description_content': 'T605F'}
#     ]

#     insert_data_into_db(db_connection=db_connection, table_name='products', data=sample_data, chunk_size=2000)
