import pandas as pd
import sqlite3

from ButterAndCrust.lib.DB.Tables.DBTable import DBTable

class SQLTable(DBTable):
    """
    An sqlite3 wrapper that for convenient use of the sqlite3 package.
    Returns queries as pandas DataFrames.
    """

    def __init__(self, table_name, columns, db_file, indices=[]):
        """
        Instantiates a new instance of the SQLTable class. 

        Args:
            table_name(``str``): name of the table
            columns(``list of str``): column names
            db_file(``str``): filepath of the database
            indices(``set of SQLTable.index``)
        """
        super().__init__(table_name, columns)
        self._conn = self.create_connection(db_file)
        self.db_file = db_file
        self._indices = indices

    def _execute(self, sql, **parameters):
        """
        Executes and commits a sql command

        Args:
            sql(``str``): sql statement

        Keyword Args:
            values(``tuple``, optional): tuple of parameters to insert 
                into the sql statement 
        """

        self.general_execute(sql, self.conn, **parameters)

    def _drop(self):
        """
        Drops entire table from the db
        """

        sql = '''DROP TABLE ''' + self.name
        self._execute(sql)

    def copy(self, new_name, contents=False):
        """
        Copies the table format and it's indices without contents

        Args:
            new_name(``str``): Name of the new table being created

        Keyword Args:
            contents(``bool``): Whether to also copy the contents of
                the table

        Returns:
            new_table(``SQLTable``): Instance of SQLTable object 
        """

        new_table = SQLTable(new_name, self.columns, self.db_file)

        where = "WHERE 1" if contents else "WHERE 0"

        # First create the table
        sql = """
            CREATE TABLE {new} AS 
            SELECT *
            FROM {copy_from} 
            {where_clause}
            ;
        """.format(
            new=new_table.name,
            copy_from=self.name,
            where_clause=where)

        self._execute(sql)
        
        try:
            # Then copy indices
            for index in self._indices:
                new_table.create_index(
                    index.name,
                    index.columns,
                    is_unique=index.is_unique
                )
        except:
            new_table._drop()
            raise

        return new_table

    def sql_to_df(self, sql):
        """
        Converts the output of a sql statement and returns it in a
        pandas dataframe.

        Args:
            sql(``str``): sql statement

        Returns:
            df(``DataFrame``) pandas dateframe of returned results
        """

        df = pd.read_sql_query(sql, self.conn)
        return df

    def select(self, columns=[], where=""):
        """
        Executes a select statement.

        Keyword Args:
            columns(``list of str``, optional): list of column names to
                query
            where(``str``, optional): where clause to filter query

        To Do: 
            Change args to kwargs
        """

        sql = '''
            SELECT {cols} FROM {name} {where_clause}
        '''.format(
            cols=','.join(columns) if columns else '*',
            name=self.name,
            where_clause="WHERE " + where if where else ""
        )

        return self.sql_to_df(sql)

    def max(self, column, where=""):
        """
        Gets the max value of a column

        Args:
            column(``str``): column name to query
        """

        sql = (
        '''
            SELECT MAX({col}) FROM {table} {where_clause}
        '''.format(
            table=self.name,
            col=column,
            where_clause="WHERE " + where if where else ""
            )
        )

        cur = self.conn.cursor()

        return cur.execute(sql).fetchall()[0][0]
    
    def min(self, column, where=""):
        """
        Gets the min value of a column

        Args:
            column(``str``): column name to query
        """

        sql = (
        '''
            SELECT MIN({col}) FROM {table} {where_clause}
        '''.format(
            table=self.name,
            col=column,
            where_clause="WHERE " + where if where else ""
            )
        )

        cur = self.conn.cursor()

        return cur.execute(sql).fetchall()[0][0]
    

    def delete(self, where=""):
        """
        Deletes from table. 

        Args:
            where(``str``, optional): where clause to filter query

        To Do:
            change args to kwargs
        """

        sql = '''
            DELETE FROM {name} {where_clause}
        '''.format(
            name=self.name,
            where="WHERE " + where if where else ""
        )

        self.general_execute(sql, self.conn)

    def insert(self, row):
        """
        Inserts a row into the table.

        Args:
            row(``dict``): row to insert.
                Must be a dictionary with column names as the key.
        """

        columns = row.keys()
        values = tuple([row[v] for v in row])

        sql = """
            INSERT INTO {table}({cols}) VALUES({vals});
        """.format(
            table=self.name,
            cols=','.join(columns),
            vals=("?,"*len(columns))[:-1]
        )

        self._execute(sql, values=values)

    def insert_many(self, rows):
        """
        Inserts many rows to table.

        Args:
            rows(``list of dict``): list rows to insert.
                Each row must be dictionary with column names as keys.
        """
        for row in rows:
            self.insert(row)

    def sync(self, rows, key):
        """
        Synchronise input values to a table. Will update existing rows
        if already exist. 

        Args:
            rows(``list of dict``): list rows to insert.
                Each row must be dictionary with column names as keys.
            key(``list of str``): column names for join key

        To Do:
            Allow key(``str``, ``list``)
        """

        # create temp table
        temp_table = self.copy("TempTable")

        try:
            # insert all values to temp table
            temp_table.insert_many(rows)

            # update existing values in self
            temp_cols = ",".join([temp_table.name + "." + col for col in self.columns])
            key_str = " AND ".join([temp_table.name + "." + col + "=" + self.name + "." + col for col in key])
            
            sql = (
                '''
                REPLACE INTO {table}
                ({cols})
                SELECT {tempcols}
                FROM {table} 
                INNER JOIN {temptable} ON {key}
                '''.format(
                        table=self.name,
                        cols=','.join(self.columns),
                        tempcols=temp_cols,
                        temptable=temp_table.name,
                        key=key_str
                    )
            )

            self._execute(sql)

            # insert new values to self
            sql = ('''
                INSERT INTO {table} ({cols})
                SELECT * FROM {temptable}
                WHERE NOT EXISTS (
                    SELECT * FROM {table} WHERE {key}
                );
                '''.format(
                    table=self.name,
                    cols=','.join(self.columns),
                    temptable=temp_table.name,
                    key=key_str
                    )
            )

            self._execute(sql)
            
            # drop temp table when complete
            temp_table._drop()

        except:
            # safely drop temp table if we hit any error after creation
            temp_table._drop()
            raise

    
    def create_index(self, name, key, is_unique=False):
        """
        Creates a non-unique index from a list of table columns

        Args:
            name(``str``): unique name for the index
            key(``list of str``): column names to index
            is_unique(``bool``, optional): bool for whether index allows
                duplicates on key

        To Do: 
            Allow key(``str``, ``list of str``)
        """

        # format uniqueness
        UNIQUE = "UNIQUE" if is_unique else ""

        sql = """
            CREATE {unique} INDEX {idx_name} ON {table}({index_cols})
        """.format(unique=UNIQUE, 
                    idx_name=name,
                    table=self.name,
                    index_cols=','.join(key))

        self._execute(sql)
        self._indices.append(self.index(name, key, is_unique))

    @property
    def conn(self):
        return self._conn

    @property
    def indices(self):
        return self._indices
    
    @staticmethod
    def create_connection(db_file):
        """ 
        create a database connection to a SQLite database.

        Args:
            db_file(``str``): filepath of database

        Returns:
            conn(``sqlite connection obj``)
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except sqlite3.Error as e:
            print(e)

        return conn

    @staticmethod
    def general_execute(sql, db_conn, **parameters):
        """
        Executes a general sql command. 

        Args:
            sql(``str``): sql query to execute
            db_conn(``sqlite connection obj``)

        Keyword Args:
            values(``tuple``, optional): tuple of parameters to insert 
                into the sql statement
        """
        cur = db_conn.cursor()

        if 'values' in parameters:
            cur.execute(sql, parameters['values'])
        else:
            cur.execute(sql)

        db_conn.commit()

    @staticmethod
    def general_query(sql, db_conn):
        """
        Executes a general sql command and returns the result to a 
        pandas DataFrame.

        Args:
            sql(``str``): sql query to execute
            db_conn(``sqlite connection obj``)
        """
        df = pd.read_sql_query(sql, db_conn)
        return df
    
    class index(object):
        """
        Object for sql table indices

        Attributes:
            _name(``str``): unique name of the index
            _columns(``list of str``): column names of index key
            _is_unique(``bool``): bool for whether index allows 
                duplicates on key
        """
        def __init__(self, name, columns, is_unique):
            """
            Instantiates a new index instance. 

            Args:
                name(``str``): unique name of the index
                columns(``list of str``): column names of index key
                is_unique(``bool``): bool for whether index allows 
                    duplicates on key

            To Do:
                Allow columns(``str``, ``list of str``)
            """
            self._name = name
            self._columns = columns
            self._is_unique = is_unique

        def __str__(self):
            """
            Overrides the default implementation
            """
            s = """
            Index: {name}
            Columns: {cols}
            Unqiue: {unique}
            """.format(
                name=self.name,
                cols=self.columns,
                unique=self.is_unique
            )

            return s

        def __eq__(self, other):
            """
            Overrides the default implementation
            """
            if isinstance(other, self.__class__):
                if self.name != other.name:
                    return False
                if self.is_unique != other.is_unique:
                    return False
                return self.columns == other.columns
            return False
        
        @property
        def name(self):
            return self._name
        
        @property
        def columns(self):
            return self._columns
        
        @property
        def is_unique(self):
            return self._is_unique
