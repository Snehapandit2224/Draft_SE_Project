import sqlalchemy

# The user has provided the password in the chat.
engine = sqlalchemy.create_engine('mysql+mysqlconnector://root:soham3217@localhost/')
with engine.connect() as conn:
    conn.execute(sqlalchemy.text("CREATE DATABASE hr_attrition_dev"))
