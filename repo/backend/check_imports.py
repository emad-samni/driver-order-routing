try:
    import fastapi
    print("FastAPI version:", fastapi.__version__)
except Exception as e:
    print("FastAPI import error:", e)

try:
    import openpyxl
    print("openpyxl version:", openpyxl.__version__)
except Exception as e:
    print("openpyxl import error:", e)

try:
    import pydantic
    print("Pydantic version:", pydantic.__version__)
except Exception as e:
    print("Pydantic import error:", e)

try:
    import sqlalchemy
    print("SQLAlchemy version:", sqlalchemy.__version__)
except Exception as e:
    print("SQLAlchemy import error:", e)
