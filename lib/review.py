import sqlite3
from lib import CONN, CURSOR

class Review:
    all = {}
    
    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id
    
    def __repr__(self):
        return f"<Review {self.id}: {self.year}, {self.summary}, Employee ID: {self.employee_id}>"
    
    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER CHECK (year >= 2000),
                summary TEXT NOT NULL,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)
        CONN.commit()
    
    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()
    
    def save(self):
        CURSOR.execute("""
            INSERT INTO reviews (year, summary, employee_id) 
            VALUES (?, ?, ?)""", (self.year, self.summary, self.employee_id))
        
        self.id = CURSOR.lastrowid
        CONN.commit()
        self.__class__.all[self.id] = self
    
    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()
        return review
    
    @classmethod
    def instance_from_db(cls, row):
        if row is None:
            return None
        review_id, year, summary, employee_id = row
        if review_id in cls.all:
            existing_review = cls.all[review_id]
            existing_review.year = year
            existing_review.summary = summary
            existing_review.employee_id = employee_id
            return existing_review
        review = cls(year, summary, employee_id, review_id)
        cls.all[review_id] = review
        return review
    
    @classmethod
    def find_by_id(cls, id):
        CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None
    
    def update(self):
        CURSOR.execute("""
            UPDATE reviews 
            SET year = ?, summary = ?, employee_id = ? 
            WHERE id = ?""", (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()
    
    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        CONN.commit()
        del self.__class__.all[self.id]
        self.id = None
    
    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]
    
    @property
    def year(self):
        return self._year
    
    @year.setter
    def year(self, value):
        if isinstance(value, str) and value.isdigit():
            value = int(value)
        if not isinstance(value, int) or value < 2000:
            raise ValueError("Year must be an integer greater than or equal to 2000.")
        self._year = value
    
    @property
    def summary(self):
        return self._summary
    
    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Summary must be a non-empty string.")
        self._summary = value
    
    @property
    def employee_id(self):
        return self._employee_id
    
    @employee_id.setter
    def employee_id(self, value):
        from lib.employee import Employee  # Avoid circular import
        if not isinstance(value, int) or not Employee.find_by_id(value):
            raise ValueError("employee_id must be a valid Employee ID from the database.")
        self._employee_id = value
