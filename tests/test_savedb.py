import pytest
import pytest_postgresql
import pytest_check as check

from savedb import truncate, save_to_temp_db, update_prod_db

TABLES = ["horse_files", "zebra_files"]
TEMP_TABLES = [f"{i}_temp" for i in TABLES]
BIN_IMAGES = [
    b"iVBORw0KGgoAAAANSUhEUgAAAOEAAADhCAIAAACx0UUtAAEAAElEQVR4nFT915YtW5IdiN",
    b"nSrn3r0HH0uSJFpSpUoVBokOyBQT6g+dCjOdhP/AL+WH8B2T2aBNENkKiqzKrKvDevPCpO6",
    b"K1dL734sE8mSH8K3yGGh7ttszmnTbON/i//559pa6213nsPwRjT9XLQhhLWdqpqOyUdIIqAOhe0cSSyzgFCEHMWRQnGWCu",
    b"rBpVlmVFWSq21BsAR43EcM8a3dFVVFgcgBJyDomDjcmStL8uyqeq",
    b"+l957a62RGgBxzkmHjZcOBcwAKAQGSQnFCKZzrLVP4pTRDBzP4knf2W",
]
NUMS = [0., 8., 5.5, 100., 999.]


def test_truncate_table(db_connection, prod_tables):
    """
        Test truncate temp tables
    """
    check.is_true(truncate(prod_tables, db_connection), "True, table successfully truncated")


def test_truncate_error_table(db_connection, temp_tables):
    """
        Test truncate not exists tables
    """
    check.is_false(truncate(temp_tables, db_connection), "False, table does not exist")


def test_save_temp(db_connection, prod_tables, bin_images):
    """
        Test save images to temp tables
    """
    check.is_true(save_to_temp_db(bin_images, prod_tables, db_connection), "True, image saved to temp table")


def test_error_save_temp(db_connection, prod_tables, temp_tables, numbers, bin_images):
    """
        Test error for save images to temp tables
    """
    check.is_false(save_to_temp_db(numbers, prod_tables, db_connection), "False, can't escape float to binary")
    check.is_false(save_to_temp_db(bin_images, temp_tables, db_connection), "False, table does not exist")


def test_update_prod(db_connection, prod_tables):
    """
        Test save images to prod tables
    """
    check.is_true(update_prod_db(prod_tables, db_connection), "True, image saved to prod table")


def test_error_update_prod(db_connection, temp_tables):
    """
        Test error for save images to prod tables
    """
    check.is_false(update_prod_db(temp_tables, db_connection), "False, relation does not exist")


@pytest.fixture(scope='function')
def db_connection(postgresql):
    """
        Create postgressql mock-connection to database
    """
    cur = postgresql.cursor()
    for table_name in TABLES + TEMP_TABLES:
        cur.execute(f"""
            CREATE TABLE {table_name} (id integer, orig_filename text, file_data bytea);
        """)
    postgresql.commit()
    cur.close()

    yield postgresql


@pytest.fixture(params=TABLES)
def prod_tables(request):
    """
        Fixture generate prod table names
    """
    yield request.param


@pytest.fixture(params=TEMP_TABLES)
def temp_tables(request):
    """
        Fixture generate temp table names
    """
    yield request.param


@pytest.fixture(params=BIN_IMAGES)
def bin_images(request):
    """
        Fixture generate temp table names
    """
    yield request.param


@pytest.fixture(params=NUMS)
def numbers(request):
    yield request.param

