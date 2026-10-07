from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI() 
# app -> object  , FastAPI -> class, FastAPI() -> constructor

connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_DATABASE"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
    
)

cursor = connection.cursor() 

class Student(BaseModel): # inheriting BaseModel class from pydantic into Student class
    id: int = None       # Also called as class based validation, which is a way to validate the data using classes and objects
    name: str = None
    course: str = None


@app.get("/students")  # decorator : function that takes another function as input and returns a new function
# Which are the http methods?  
# GET, POST, PUT, DELETE, PATCH
# GET : Client gets data from the server
# POST : Client sends data to the server
# PUT : Client updates data (complete) on the server
# DELETE : Client deletes data from the server
# PATCH : Client partially updates data on the server
def get_all_students():
    cursor.execute("SELECT * FROM students")  # execute the query
    rows = cursor.fetchall()  # fetch all the rows
    print(rows)  # print the rows

    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "name": row[1],
            "course": row[2]
        })
    return result   
@app.get("/students/{id}")  # path parameter
def get_student_by_id(id: int): # type hinting : int -> integer ---done by pydantic
    cursor.execute("SELECT * FROM students WHERE id = %s", (id,))  # execute the query---using parameterized query to prevent SQL injection
    row = cursor.fetchone()  # fetch one row
    try:
            return {
                "id": row[0],
                "name": row[1],
                "course": row[2]
            }
    except:
        raise HTTPException(status_code=404, detail="Student not found") #

@app.post("/students")  # decorator : function that takes another function as input and returns a new function
def create_student_record(student: Student):  # type hinting : Student -> Student object
    
    try:
         
        cursor.execute("INSERT INTO students (id, name, course) VALUES (%s, %s, %s)", (student.id, student.name, student.course))
        connection.commit()  # commit the transaction
        raise HTTPException(status_code=201, detail="Student created")  # return the created student record
    except psycopg2.IntegrityError:
        connection.rollback()  # rollback the transaction
        raise HTTPException(status_code=400, detail="Student with this ID already exists")  # return the error message

# UPDATE STUDENT RECORD
@app.put("/students/{id}")  # decorator : function that takes another function as input and returns a new function
#{id} -> path parameter
def update_student_record(id: int, student: Student):
    
        cursor.execute("UPDATE students SET id = %s, name = %s, course = %s WHERE id = %s", (student.id, student.name, student.course, id))
        if(cursor.rowcount == 0):
                raise HTTPException(status_code=404, detail="invalid ID")
        connection.commit()  # commit the transaction
        raise HTTPException(status_code=200, detail="Student Record updated")     # return the updated student record

# USING PATCH METHOD TO UPDATE STUDENT RECORD
@app.patch("/students/{id}")
def patch_student_record(id: int, student: Student):
    if (student.id != None):
        cursor.execute("UPDATE students SET id = %s WHERE id = %s", (student.id, id))
    if (student.name != None):
        cursor.execute("UPDATE students SET name = %s WHERE id = %s", (student.name, id))
    if (student.course != None):
        cursor.execute("UPDATE students SET course = %s WHERE id = %s", (student.course, id))
    if(cursor.rowcount == 0):
        raise HTTPException(status_code=404, detail="invalid ID")
    connection.commit()
    raise HTTPException(status_code=200, detail="Student Record updated")

# DELETE STUDENT RECORD
@app.delete("/students/{id}")
def delete_student_record(id: int):
    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    if(cursor.rowcount == 0):
        raise HTTPException(status_code=404, detail="invalid ID")
    connection.commit()
    raise HTTPException(status_code=200, detail="Student Record deleted")