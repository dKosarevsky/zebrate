import os
import base64
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']


def truncate(table):
    """ truncate temp table """
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        with conn:
            curs = conn.cursor()
            curs.execute(f"TRUNCATE TABLE {table}_temp")

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def save_to_temp_db(image, table, image_name='img'):
    """ insert a BLOB into a temp table """
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        with conn:
            curs = conn.cursor()
            curs.execute(f"""
                INSERT INTO {table}_temp (orig_filename, file_data)
                VALUES ('img', {psycopg2.Binary(image)})
            """)
            conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print('save to temp error:!')
        print(error)


def update_prod_db(table):
    """ update prod table """
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        with conn:
            curs = conn.cursor()
            curs.execute(f"""
                INSERT INTO {table}(orig_filename, file_data)
                    SELECT DISTINCT orig_filename, file_data
                    FROM {table}_temp temp
                    WHERE NOT EXISTS (
                            SELECT 1
                            FROM {table} prod
                            WHERE temp.file_data = prod.file_data
                    )
            """)
            conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print('update error:!')
        print(error)


def save_img(data, filename):
    with open(filename, "wb") as fh:
        fh.write(base64.decodebytes(data))


def load(table, path_to_dir, img_id, ext=".png"):
    """ read BLOB data from a table """
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        with conn:
            curs = conn.cursor()
            curs.execute(f"""
                SELECT orig_filename, file_data
                FROM {table}
                WHERE id = {img_id}
            """)

            blob = curs.fetchone()
            print(path_to_dir + ext)
            save_img(blob[1], path_to_dir + blob[0] + ext)

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def main():
    # load("zebra_files", path_to_dir="./imgs/", img_id=9)
    pass


if __name__ == "__main__":
    main()
