from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker


# DATABASE MODULE SETUP
# create database and table
engine = create_engine('sqlite:///todo.db?check_same_thread=False')
Base = declarative_base()


class Table(Base):  # model class for table in database
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String)
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.task


# actually create table
Base.metadata.create_all(engine)


# PROGRAM FUNCTIONS AND CONSTANTS
WEEKDAY_DICT = {
    0: 'Monday',
    1: 'Tuesday',
    2: 'Wednesday',
    3: 'Thursday',
    4: 'Friday',
    5: 'Saturday',
    6: 'Sunday'
}


def print_menu():
    """Prints the program menu."""
    print()
    print("1) Today's tasks")
    print("2) Week's tasks")
    print('3) All tasks')
    print('4) Missed tasks')
    print('5) Add task')
    print('6) Delete task')
    print('0) Exit')


def print_day_tasks(session_object, day: datetime):
    """Prints all the tasks on the list for the given day (datetime object)."""
    rows = session_object.query(Table).filter(Table.deadline == day.date()).all()

    month_day = day.strftime('%#d %b')
    print(WEEKDAY_DICT[day.weekday()], month_day)

    if rows:
        counter = 1
        for row in rows:
            print(f'{counter}. {row.task}')
            counter += 1
    else:
        print('Nothing to do!')


def print_week_tasks(session_object):
    """Prints all the tasks on the list between the current day and 7 days in
    the future."""
    day_in_question = datetime.today()
    counter = 0
    while counter < 7:
        if counter > 0:
            print()
        print_day_tasks(session_object, day_in_question)
        day_in_question += timedelta(days=1)
        counter += 1


def print_all_tasks(session_object):
    """Prints all tasks on the to-do list, ordered by deadline.
    Returns a sorted list of tuples of all tasks & their deadlines."""
    rows = session_object.query(Table).order_by(Table.deadline).all()
    all_tasks = {}  # for sorting & printing
    for row in rows:
        all_tasks[row.task] = row.deadline

    # print
    return_tasks = []
    if rows:
        counter = 1
        for task, deadline in all_tasks.items():
            print(f"{counter}. {task}. {deadline.strftime('%#d %b')}")
            return_tasks.append(task)
            counter += 1
    else:
        print('Nothing to do!')
    return return_tasks


def print_missed_tasks(session_object):
    """Prints a list of all missed tasks, ordered by deadline."""
    today = datetime.today()
    rows = session_object.query(Table).filter(Table.deadline < today).order_by(Table.deadline)
    missed_tasks = {}  # for sorting & printing
    for row in rows:
        missed_tasks[row.task] = row.deadline

    print('Missed tasks:')
    if rows:
        counter = 1
        for task, deadline in missed_tasks.items():
            print(f"{counter}. {task}. {deadline.strftime('%#d %b')}")
            counter += 1
    else:
        print('Nothing is missed!')


def add_task(session_object):
    """Adds a task to the list from user input."""
    task_name = input('Enter task: ')
    task_deadline = input('Enter deadline: ').strip()
    deadline = datetime.strptime(task_deadline, '%Y-%m-%d')
    new_row = Table(task=task_name, deadline=deadline.date())
    session_object.add(new_row)
    session_object.commit()
    print('The task has been added!')


def delete_task(session_object):
    """Shows user a list of all tasks, then deletes a task selected by user."""
    # num_rows = session_object.query(Table).count()
    # print(f'BEFORE deletion: number of rows in table = {num_rows}')
    with engine.connect() as con:
        print('Choose the number of the task you want to delete:')
        list_of_tasks = print_all_tasks(session_object)  # see print_all_tasks docstring
        if list_of_tasks:
            number_to_delete = int(input().strip())
            task_to_delete = list_of_tasks[number_to_delete - 1]
            # session_object.query(Table).filter(Table.task == task_to_delete).delete()
            con.execute(f'DELETE FROM task WHERE task = "{task_to_delete}"')
            print('The task has been deleted!')
            # num_rows = session_object.query(Table).count()
            # print(f'AFTER deletion: number of rows in table = {num_rows}')
        else:
            print('No tasks to delete!')


if __name__ == '__main__':
    Session = sessionmaker(bind=engine)
    session = Session()

    # MAIN PROGRAM LOOP
    while True:
        print_menu()
        action = input().strip()
        print()

        if action == '0':  # exit
            session.close()
            print('Bye!')
            break
        elif action == '1':  # today's tasks
            print_day_tasks(session, datetime.today())
        elif action == '2':  # week's tasks
            print_week_tasks(session)
        elif action == '3':  # all tasks
            print('All tasks:')
            print_all_tasks(session)
        elif action == '4':  # missed tasks
            print_missed_tasks(session)
        elif action == '5':  # add task
            add_task(session)
        elif action == '6':  # delete task
            delete_task(session)
        else:
            print()
            print('Invalid input')
