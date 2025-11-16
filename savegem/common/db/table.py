from typing import TYPE_CHECKING, Callable, Iterator

if TYPE_CHECKING:
    from savegem.common.db.manager import DatabaseManager


class DatabaseRow:
    """
    Table row object.
    Used to perform operations on row data.
    """

    def __init__(self, row_number: int, data: tuple, columns: list[str]):

        self.__row_number = row_number
        self.__data = {}
        self.__edits = {}
        self.__is_new = False

        for index in range(len(columns)):
            column_value = None

            if len(data) > index:
                column_value = data[index]

            self.__data[columns[index].lower()] = column_value

    def get(self, column_name: str):
        """
        Used to get column value from row.
        """
        return self.__data.get(column_name.lower())

    def set(self, column_name: str, column_value):
        """
        Used to set column value for row.
        """
        self.__edits[column_name] = column_value

    @property
    def is_new(self):
        """
        Used to check if row has been inserted
        or if it was retrieved from database.
        """
        return self.__is_new

    @is_new.setter
    def is_new(self, is_new: bool):
        """
        Used to mark row as new and
        vice versa.
        """
        self.__is_new = is_new

    @property
    def edits(self):
        """
        Used to get all row edits.
        Map of column name -> column value.
        """
        return self.__edits

    @property
    def row_number(self):
        """
        Used to get number of row.
        """
        return self.__row_number

    def has_edits(self):
        """
        Used to check whether row has
        any edits.
        """
        return len(self.__edits) > 0

    def _apply_edits(self):
        """
        Used to apply edits to table row.
        """

        self.__data = {**self.__data, **self.__edits}
        self.__edits.clear()

    def to_json(self):
        """
        Used to get row data in
        JSON format.
        """
        return self.__data


class DatabaseTable:
    """
    Database table wrapper.
    Used to perform operations on table
    data.
    """

    def __init__(self, db: "DatabaseManager",  table_name: str):
        self.__db = db
        self.__record_counter = 0
        self.__where_clause = None
        self.__where_clause_args = []
        self.__order_by_clause = None
        self.__table_name = table_name
        self.__records: list[DatabaseRow] = []
        self.__deleted_records: list[DatabaseRow] = []
        self.__columns: list[str] = []

    def __iter__(self) -> Iterator[DatabaseRow]:
        return iter(self.__records)

    def where(self, where_clause: str, *args):
        """
        Used to apply WHERE clause filter
        that would be used to retrieve table data.
        """

        self.__where_clause = where_clause
        self.__where_clause_args = args

        return self

    def order_by(self, order_by_clause: str):
        """
        Used to set ORDER BY clause.
        Allows to sort table data when retrieving
        from database.
        """

        self.__order_by_clause = order_by_clause

        return self

    def retrieve(self):
        """
        Used to retrieve table data
        from database.
        """

        sql = f"SELECT * FROM {self.__table_name}"
        retrieve_args = tuple()

        if self.__where_clause is not None:
            sql += f" WHERE {self.__where_clause}"
            retrieve_args = tuple(self.__where_clause_args)

        if self.__order_by_clause is not None:
            sql += f" ORDER BY {self.__order_by_clause}"

        cursor = self.__db.select(sql, retrieve_args)
        self.__columns = [str(description[0]).lower() for description in cursor.description]
        self.__records.clear()
        self.__record_counter = 0

        for row_data in cursor.fetchall():
            self.__record_counter += 1
            self.__records.append(DatabaseRow(self.__record_counter, row_data, self.__columns))

        return self

    @property
    def is_empty(self) -> bool:
        return len(self.rows) == 0

    @property
    def rows(self) -> list[DatabaseRow]:
        """
        Used to get list of table rows.
        """
        return self.__records

    @property
    def columns(self) -> list[str]:
        """
        Used to get list of table column names.
        """
        return self.__columns

    def add_row(self):
        """
        Used to add row to the table.
        Will not immediately persist row in database
        but just add it to the object.
        """

        self.__record_counter += 1
        row = DatabaseRow(self.__record_counter, tuple(), self.__columns)
        row.is_new = True

        self.__records.append(row)
        return row.row_number

    def get_first(self, column_name: str):
        """
        Used to get column value of first row
        in dataset.
        """
        return self.get(1, column_name)

    def set_first(self, column_name: str, column_value):
        """
        Used to set column value of first row
        in dataset.
        """
        self.set(1, column_name, column_value)

    def get(self, row_number: int, column_name: str):
        """
        Used to get column value of specific
        table row.
        """

        for record in self.__records:
            if record.row_number == row_number:
                return record.get(column_name)

        return None

    def set(self, row_number: int, column_name: str, column_value):
        """
        Used to set column value of specific
        table row.
        """

        for record in self.__records:
            if record.row_number == row_number:
                record.set(column_name, column_value)

    def save(self):
        """
        Used to persist changes that were made
        to table data in database.
        """

        self.__delete_records()
        self.__update_records()
        self.__insert_records()

    def remove(self, row_number: int):
        """
        Used to remove record that corresponds
        provided row number.
        """
        self.__remove_internal(lambda record: record.row_number == row_number)
        return self

    def remove_all(self):
        """
        Used to remove all records from the table.
        """
        self.__remove_internal(lambda record: True)
        return self

    def __delete_records(self):
        """
        Part of save process.
        Used to delete records in database.
        """

        pk_columns = self.__get_pk_columns()
        pk_filter_single = " AND ".join([f"{column} = ?" for column in pk_columns])
        pk_filter_sql = []
        pk_filter_values = []

        if len(self.__deleted_records) == 0:
            return

        for record in self.__deleted_records:
            for pk_column in pk_columns:
                pk_filter_values.append(record.get(pk_column))

            pk_filter_sql.append(f"({pk_filter_single})")

        self.__db.execute(f"""
            DELETE FROM {self.__table_name}
            WHERE {" OR ".join(pk_filter_sql)}
        """, tuple(pk_filter_values))

        self.__deleted_records.clear()

    def __update_records(self):
        """
        Part of save process.
        Used to update records in database.
        """

        pk_columns = self.__get_pk_columns()

        for record in self.__records:
            if not record.has_edits() or record.is_new:
                continue

            update_fields = ", ".join([f"{column_name} = ?" for column_name in record.edits.keys()])
            values = tuple(record.edits.values())

            sql = f"""
                UPDATE {self.__table_name} 
                SET {update_fields}
            """

            if len(pk_columns) > 0:
                filter_conditions = []
                filter_values = []

                for pk_column in pk_columns:
                    filter_conditions.append(f"{pk_column} = ?")
                    filter_values.append(record.get(pk_column))

                sql += f" WHERE {" AND ".join(filter_conditions)}"
                values += tuple(filter_values)

            self.__db.execute(sql, values)
            record._apply_edits()  # noqa

    def __insert_records(self):
        """
        Part of save process.
        Used to insert new records into database.
        """

        for record in self.__records:
            if not record.is_new:
                continue

            insert_field_names = ", ".join([column_name for column_name in record.edits.keys()])
            insert_field_placeholders = ", ".join(["?" for _ in record.edits.keys()])
            insert_field_values = tuple([column_value for column_value in record.edits.values()])

            sql = f"""
                INSERT INTO {self.__table_name} ({insert_field_names})
                VALUES ({insert_field_placeholders})
            """

            self.__db.execute(sql, insert_field_values)
            record._apply_edits()  # noqa
            record.is_new = False

    def __remove_internal(self, remove_condition: Callable[[DatabaseRow], bool]):
        """
        Internal row remove method.
        Remove all records that match provided condition.
        """

        for record in self.__records:
            if remove_condition(record):
                self.__deleted_records.append(record)

        for record in self.__deleted_records:
            self.__records.remove(record)

    def __get_pk_columns(self):
        """
        Used to get name of primary key column
        of table.
        """

        cursor = self.__db.select(f"PRAGMA table_info({self.__table_name})")
        columns = cursor.fetchall()
        pk_columns = []

        for col in columns:
            cid, name, type_, notnull, default_value, pk = col
            if pk:
                pk_columns.append(name)

        return pk_columns
