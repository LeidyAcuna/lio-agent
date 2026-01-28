from core.database import ManagerDB
from services.llm import test_ollama
from core.database import ManagerDB

def main():
    manager_db = ManagerDB()
    print("Hello from lio-agent!")
    manager_db.init_db()
    print("DB inicialized succesfully!")

    obj_expense = test_ollama()
    manager_db.insert_row_in_db(user_id=134324, object=obj_expense)

    




if __name__ == "__main__":
    main()
