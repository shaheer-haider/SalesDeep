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
        print(f"Connecting to database {database} on {host}:{port} as {user}")
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
        )
        print("Database connection successful")
        return connection
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def store_products(products):
    """
    Stores the products in the database.
    """
    connection = get_db_connection()
    if not connection:
        return

    try:
        with connection.cursor() as cursor:
            for product in products:
                cursor.execute(
                    """
                    INSERT INTO `salesdeep`.`products`
                    (`product_id`,
                    `sku`,
                    `name`,
                    `model`,
                    `brand`,
                    `type`,
                    `price`,
                    `currency`,
                    `weight`,
                    `length`,
                    `width`,
                    `height`,
                    `diameter`,
                    `leading`,
                    `image`,
                    `description_html`,
                    `description`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    sku=VALUES(sku), name=VALUES(name), model=VALUES(model), brand=VALUES(brand), type=VALUES(type), price=VALUES(price), currency=VALUES(currency), weight=VALUES(weight), length=VALUES(length), width=VALUES(width), height=VALUES(height), diameter=VALUES(diameter), `leading`=VALUES(`leading`), image=VALUES(image), description_html=VALUES(description_html), description=VALUES(description)
                    """,
                    (
                        product["product_id"],
                        product["sku"],
                        product["name"],
                        product["model"],
                        product["brand"],
                        product["type"],
                        product["price"],
                        product["currency"],
                        product["weight"],
                        product["length"],
                        product["width"],
                        product["height"],
                        product["diameter"],
                        product["leading"],
                        product["image"],
                        product["description_html"],
                        product["description"]
                    )
                )
            connection.commit()
    except Exception as e:
        print(f"Error storing products: {e}")
    finally:
        connection.close()
