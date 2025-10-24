from sqlite3 import Connection


class TableDDL:
    """
    Used to create DDL of the table
    that is already in database.

    Allows to extend DDL by adding foreign keys.
    """

    def __init__(self, connection: Connection, table_name: str):
        self.__connection = connection
        self.__original_table_name = table_name
        self.__columns_ddl = []
        self.__foreign_key_ddl = []
        self.__primary_key_ddl = None

        self.__get_table_column_ddl()
        self.__get_foreign_key_ddl()

    def build(self):
        """
        Used to build table DDL as string.
        """

        ddl_list = []

        for column_ddl in self.__columns_ddl:
            ddl_list.append(column_ddl)

        if self.__primary_key_ddl is not None:
            ddl_list.append(self.__primary_key_ddl)

        for fk_ddl in self.__foreign_key_ddl:
            ddl_list.append(fk_ddl)

        return f"""
            CREATE TABLE {self.__original_table_name} (
               {",\n".join(ddl_list)}
            )
        """

    def add_foreign_key(self, from_cols: list[str], fk_table: str, to_cols: list[str], on_delete: str, on_update: str):
        """
        Used to add foreign key to DDL definition.
        """

        self.__foreign_key_ddl.append(f"""
            FOREIGN KEY ({", ".join(from_cols)}) REFERENCES {fk_table}({", ".join(to_cols)})
                ON DELETE {on_delete}
                ON UPDATE {on_update}
        """)

    def __get_table_column_ddl(self):
        """
        Used to get existing table columns DDL.
        Also used to get primary key DDL.
        """

        cursor = self.__connection.cursor()
        table_info = cursor.execute(f"PRAGMA table_info({self.__original_table_name})").fetchall()
        pk_columns = []

        # Collect and format table DDL.
        for _, name, data_type, not_null, default, pk in table_info:
            if pk > 0:
                pk_columns.append(name)

            column_ddl = f"        {name} {data_type}"

            if not_null == 1:
                column_ddl += " NOT NULL"

            if default is not None:
                column_ddl += f" DEFAULT {default}"

            self.__columns_ddl.append(column_ddl)

        if len(pk_columns) > 0:
            self.__primary_key_ddl = f"PRIMARY KEY ({", ".join(pk_columns)})"

    def __get_foreign_key_ddl(self):
        """
        Used to get existing foreign key DDL.
        """

        cursor = self.__connection.cursor()
        foreign_key_info = cursor.execute(f"PRAGMA foreign_key_list({self.__original_table_name})").fetchall()

        fk_table_map = {}
        from_col_map = {}
        to_col_map = {}

        on_delete_map = {}
        on_update_map = {}

        # Collect existing foreign key info.
        for fk_id, _, fk_table, from_col, to_col, on_update, on_delete, _ in foreign_key_info:

            from_cols = from_col_map.get(fk_id, [])
            to_cols = to_col_map.get(fk_id, [])

            from_cols.append(from_col)
            to_cols.append(to_col)

            from_col_map[fk_id] = from_cols
            to_col_map[fk_id] = to_cols

            fk_table_map[fk_id] = fk_table
            on_update_map[fk_id] = on_update
            on_delete_map[fk_id] = on_delete

        for fk_id in fk_table_map.keys():
            fk_table = fk_table_map.get(fk_id)
            from_cols = from_col_map.get(fk_id)
            to_cols = to_col_map.get(fk_id)
            on_update = on_update_map.get(fk_id)
            on_delete = on_delete_map.get(fk_id)

            self.add_foreign_key(
                from_cols,
                fk_table,
                to_cols,
                on_delete,
                on_update
            )
