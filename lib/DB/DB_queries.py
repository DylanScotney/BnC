import sqlite3
import pandas as pd
from datetime import timedelta

def select_all(table_name, db_conn):
    """
    Query all rows in a given table.

    :param table_name:    (str) name of the table
    :param db_conn:       (sqlite3 connection object)
    """

    sql = '''SELECT * FROM ''' + table_name

    return sql_to_df(sql, db_conn)

def select_all_by_delivery_date(table_name, start_date, end_date, db_conn):
    """
    Selects all the orders in a given table between start_date and 
    end_date and returns as a pandas df.

    :param table_name:          (str) name of the table to query
    :param start_date:          (datetime) intial date of orders to get
    :param end_date:            (datetime) final date of orders to get
    :param db_conn:             (sqlite connection object)

    Note: this requires the table to have column "DeliveryDate"
    """

    sql = (
    '''
        SELECT *
        FROM {table}
        WHERE DeliveryDate >= date('{i_date}') 
        AND DeliveryDate <= date('{f_date}')
    '''.format(
            table=table_name,
            i_date=start_date,
            f_date=end_date
        )
    )

    return sql_to_df(sql, db_conn)

def delete_all(table_name, db_conn):
    """
    Deletes all values from a table

    :param table_name:      (str) name of table
    :param db_conn:         (sqlite connection object)
    """

    sql = (
    '''
        DELETE FROM {table} WHERE 1
    '''.format(table=table_name)
    )

    cur = db_conn.cursor()
    cur.execute(sql)
    db_conn.commit()

def get_max_value(table_name, column, db_conn):
    """
    Gets the most recent delivery date in the input table

    :param table_name:      (str) name of table to query
    :param column:          (str) name of column to query
    :param db_conn:         (sqlite connection object)
    """

    sql = (
    '''
        SELECT MAX({col}) FROM {table}
    '''.format(table=table_name, col=column)
    )

    cur = db_conn.cursor()

    return cur.execute(sql).fetchall()[0][0]

def get_most_recent_order_by_email(delivery_date, db_conn):
    """
    Gets the most recent order by email that was delivered less than 
    5 weeks ago.

    :param delivery_date:   (datetime) the current delivery date
    :param db_conn:         (sqlite connection object)
    """

    cut_off_date = delivery_date - timedelta(weeks=4)

    sql = (
    '''
    SELECT ID, Email, DeliveryDate, Lineitems
    FROM
    (
        SELECT 
            ID,
            Email, 
            DeliveryDate,
            Lineitems,
            MAX(DeliveryDate) OVER (PARTITION BY Email) MaxDeliveryDate
        FROM
        (
            SELECT 
                ID,
                Email, 
                DeliveryDate,
                Lineitems 
            FROM CompressedOrderHistory
            WHERE DeliveryDate < date('{d_date}') 
            AND DeliveryDate >= date('{c_date}')
        )
    )
    WHERE DeliveryDate = MaxDeliveryDate
    '''.format(
            d_date=delivery_date,
            c_date=cut_off_date
        )
    )

    return sql_to_df(sql, db_conn)


def sql_to_df(sql, db_conn):
    """
    Converts the output of a sql statement and returns it in a pandas
    dataframe.

    :param sql:         (str) string of sql statement to execute
    :param db_conn:     (sqlite connection object)
    """

    df = pd.read_sql_query(sql, db_conn)
    return df

def create_connection(db_file):
    """ 
    create a database connection to the SQLite database specified by db_file

    :param db_file: database file

    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)

    return conn

def insert_values(table_name, columns, values, db_conn):
    """
    Insert values into the TestTable

    :param table_name:  (str) name of table to insert values
    :param columns:     (list of str) of column names
    :param row:         (set) of values to insert
    :param db_conn:     (sqlite3 connection object)

    :return:
    """

    sql = (
        "INSERT INTO {table}({cols}) VALUES({vals})"
    ).format(
        table=table_name,
        cols=','.join(columns),
        vals=("?,"*len(columns))[:-1]
    )

    cur = db_conn.cursor()
    cur.execute(sql, values)
    db_conn.commit()

    return cur.lastrowid

def drop_table(table_name, db_conn):
    """
    Drops entire table from the db

    :param table_name:      (str) table name
    :param db_conn:         (sqlite3 connection object)

    """

    sql = '''DROP TABLE ''' + table_name
    cur = db_conn.cursor()
    cur.execute(sql)
    db_conn.commit()

def create_index(table_name, index_name, index_columns, db_conn, is_unique=False):
    """
    Creates a non-unique index from a list of table columns

    :param table_name:      (str) name of the table
    :param index_name:      (str) name of the index
    :param index_columns:   (list) of columns to index
    :param db_conn:         (sqlite connection object)
    :param unique:          (bool) whether index should be unique
    """

    # format uniqueness
    UNIQUE = "UNIQUE" if is_unique else ""

    sql = ("CREATE {unique} INDEX {idx_name} ON {table}({index_cols})"
          .format(unique=UNIQUE, 
                  idx_name=index_name,
                  table=table_name,
                  index_cols=','.join(index_columns)))

    cur = db_conn.cursor()
    cur.execute(sql)

def sync_table(table_name, columns, all_values, db_conn):
    """
    Will synchronise input values to a table keyed off ID. Will update
    existing columns and add new ones

    :param table_name:      (str) table name to sync to
    :param columns:         (list of str) of column names in table_name
    :param all_values:      (list of sets) of the values to insert
    :param db_conn:         (sqlite connection object)

    """

    cur = db_conn.cursor()

    # First create a temp table 
    sql = (
        '''
        CREATE TABLE TempTable AS 
        SELECT *
        FROM {table}
        WHERE 0;
        '''.format(table=table_name)
    )
    cur.execute(sql)

    # Do in try block so we can safely drop temp table on failure
    try:
        # sqlite can't copy PK so create a temp unique index that will act as one
        create_index("TempTable", "temp_index", ["ID"], db_conn, is_unique=True)
        
        # insert all values to temp table
        for values in all_values:
            insert_values("TempTable", columns, values, db_conn)


        # update existing values
        temp_cols = ('TempTable.' 
                    + 'TempTable.'.join([col + "," for col in columns])[:-1])
        
        sql = (
            '''
            REPLACE INTO {table}
            ({cols})
            SELECT {tempcols}
            FROM {table} 
            INNER JOIN TempTable ON TempTable.ID = {table}.ID
            '''.format(
                    table=table_name,
                    cols=','.join(columns),
                    tempcols=temp_cols
                )
        )

        cur.execute(sql)

        # insert new values
        sql = ('''
            INSERT INTO {table} ({cols})
            SELECT * FROM TempTable
            WHERE NOT EXISTS (
                SELECT * FROM {table} WHERE TempTable.ID = {table}.ID
            );
            '''.format(
                table=table_name,
                cols=','.join(columns))
        )

        cur.execute(sql)

    except:
        # safely drop temp table if we hit any error after creation
        drop_table("TempTable", db_conn)
        raise

    # drop temp table when complete
    drop_table("TempTable", db_conn)
    db_conn.commit()
