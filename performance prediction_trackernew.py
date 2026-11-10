"""
STUDENT PERFORMANCE PREDICTION SYSTEM
-------------------------------------
A simple console program that stores student records and predicts
the expected performance (score, grade and risk level) using a
weighted formula on test marks, attendance, assignments and study hours.


"""

DATA_FILE = "students.txt"

# Tuple of grade boundaries: (minimum score, grade)
GRADE_TABLE = ((80, "A"), (65, "B"), (50, "C"), (40, "D"))


# ---------------------------------------------------------------
# Custom exception (Module 5)
# ---------------------------------------------------------------
class InvalidInputError(Exception):
    """Raised when a value is outside its allowed range."""
    pass


# ---------------------------------------------------------------
# Classes (Module 4 and 5)
# ---------------------------------------------------------------
class Student:
    """Parent class: a regular student."""

    def __init__(self, roll, name, attendance, study_hours, assignment, marks):
        if attendance < 0 or attendance > 100:
            raise InvalidInputError("Attendance must be between 0 and 100.")
        if study_hours < 0 or study_hours > 24:
            raise InvalidInputError("Study hours must be between 0 and 24.")
        if assignment < 0 or assignment > 100:
            raise InvalidInputError("Assignment score must be between 0 and 100.")
        if len(marks) == 0:
            raise InvalidInputError("Enter at least one test mark.")
        for m in marks:
            if m < 0 or m > 100:
                raise InvalidInputError("Test marks must be between 0 and 100.")

        self.roll = roll
        self.name = name
        self.attendance = attendance      # percentage
        self.study_hours = study_hours    # hours per day
        self.assignment = assignment      # average out of 100
        self.marks = marks                # list of test marks out of 100

    # ----- calculations -----
    def calculate_score(self, marks_list):
        """Weighted score out of 100."""
        test_avg = sum(marks_list) / len(marks_list)
        study_percent = min(self.study_hours / 5 * 100, 100)   # 5 hrs/day = full marks
        score = (0.5 * test_avg
                 + 0.2 * self.attendance
                 + 0.2 * self.assignment
                 + 0.1 * study_percent)
        return round(score, 2)

    def current_score(self):
        return self.calculate_score(self.marks)

    def predict_next_mark(self):
        """Predict the next test mark from the trend of previous marks."""
        if len(self.marks) == 1:
            return self.marks[0]
        average_change = (self.marks[-1] - self.marks[0]) / (len(self.marks) - 1)
        predicted = self.marks[-1] + average_change
        if predicted > 100:
            predicted = 100
        if predicted < 0:
            predicted = 0
        return round(predicted, 1)

    def predicted_score(self):
        """Score after adding the predicted next test mark."""
        return self.calculate_score(self.marks + [self.predict_next_mark()])

    def predicted_grade(self):
        score = self.predicted_score()
        for limit, grade in GRADE_TABLE:
            if score >= limit:
                return grade
        return "F"

    def trend(self):
        if len(self.marks) == 1:
            return "Not enough data"
        if self.marks[-1] > self.marks[0]:
            return "Improving"
        elif self.marks[-1] < self.marks[0]:
            return "Declining"
        return "Steady"

    # ----- methods that child classes will override -----
    def student_type(self):
        return "Regular"

    def required_score(self):
        """Minimum score the student should maintain."""
        return 40

    def risk_level(self):
        score = self.predicted_score()
        target = self.required_score()
        if score < target:
            return "HIGH"
        elif score < target + 15:
            return "MEDIUM"
        return "LOW"

    def advice(self):
        tips = []
        if self.attendance < 75:
            tips.append("Improve attendance (aim for at least 75%).")
        if self.study_hours < 2:
            tips.append("Increase daily study time to 2-3 hours.")
        if self.assignment < 60:
            tips.append("Submit assignments regularly and score better in them.")
        if self.trend() == "Declining":
            tips.append("Your test marks are falling - revise weak topics.")
        if len(tips) == 0:
            tips.append("Great work! Keep it up.")
        return tips

    # ----- file / display -----
    def to_line(self):
        marks_text = ",".join(str(m) for m in self.marks)
        return (f"{self.student_type()}|{self.roll}|{self.name}|{self.attendance}|"
                f"{self.study_hours}|{self.assignment}|{marks_text}")

    def __str__(self):
        return (f"{self.roll:<6} {self.name:<15} {self.student_type():<12} "
                f"{self.current_score():>6.2f}  {self.predicted_score():>6.2f}  "
                f"{self.predicted_grade():<5} {self.risk_level()}")


class ScholarshipStudent(Student):
    """Child class: scholarship students must maintain a higher score."""

    def student_type(self):              # method overriding
        return "Scholarship"

    def required_score(self):            # method overriding
        return 60

    def advice(self):                    # method overriding + super()
        tips = super().advice()
        if self.predicted_score() < self.required_score():
            tips.append("Warning: your scholarship may be at risk (need 60+).")
        return tips


def create_student(kind, roll, name, attendance, study_hours, assignment, marks):
    """Return the right type of object (polymorphism)."""
    if kind == "Scholarship":
        return ScholarshipStudent(roll, name, attendance, study_hours, assignment, marks)
    return Student(roll, name, attendance, study_hours, assignment, marks)


class StudentManager:
    """Keeps all students and handles the file."""

    def __init__(self):
        self.students = []
        self.load_data()

    def load_data(self):
        try:
            file = open(DATA_FILE, "r")
            for line in file:
                line = line.strip()
                if line == "":
                    continue
                p = line.split("|")
                marks = [float(x) for x in p[6].split(",")]
                s = create_student(p[0], p[1], p[2], float(p[3]),
                                   float(p[4]), float(p[5]), marks)
                self.students.append(s)
            file.close()
        except FileNotFoundError:
            pass    # first run, no file yet
        except (ValueError, IndexError, InvalidInputError):
            print("Warning: some data in the file was damaged and was skipped.")

    def save_data(self):
        file = open(DATA_FILE, "w")
        for s in self.students:
            file.write(s.to_line() + "\n")
        file.close()

    def find(self, roll):
        for s in self.students:
            if s.roll == roll:
                return s
        return None

    def add_student(self, student):
        self.students.append(student)
        self.save_data()

    def delete_student(self, roll):
        s = self.find(roll)
        if s is None:
            return False
        self.students.remove(s)
        self.save_data()
        return True


# ---------------------------------------------------------------
# Functions for the menu (Module 2)
# ---------------------------------------------------------------
def show_menu():
    print("\n" + "=" * 46)
    print("   STUDENT PERFORMANCE PREDICTION SYSTEM")
    print("=" * 46)
    print("1. Add a student")
    print("2. View all students")
    print("3. Predict performance of one student")
    print("4. Class summary")
    print("5. Show students at risk")
    print("6. Delete a student")
    print("7. Exit")


def add_student_screen(manager):
    try:
        roll = input("Roll number: ").strip()
        if roll == "":
            print("Roll number cannot be empty.")
            return
        if manager.find(roll) is not None:
            print("A student with this roll number already exists.")
            return
        name = input("Name: ").strip().replace("|", "-")
        if name == "":
            print("Name cannot be empty.")
            return

        kind_choice = input("Scholarship student? (y/n): ").strip().lower()
        if kind_choice == "y":
            kind = "Scholarship"
        else:
            kind = "Regular"

        attendance = float(input("Attendance percentage (0-100): "))
        study_hours = float(input("Average study hours per day: "))
        assignment = float(input("Average assignment score (0-100): "))
        marks_text = input("Test marks out of 100, separated by commas (e.g. 60,70,75): ")
        marks = [float(x) for x in marks_text.split(",")]

        student = create_student(kind, roll, name, attendance,
                                 study_hours, assignment, marks)
        manager.add_student(student)
        print("Student added successfully!")
    except InvalidInputError as e:
        print("Error:", e)
    except ValueError:
        print("Invalid input! Please enter numbers where required.")


def view_all_screen(manager):
    if len(manager.students) == 0:
        print("\nNo students recorded yet.")
        return
    print("\n" + "-" * 70)
    print(f"{'Roll':<6} {'Name':<15} {'Type':<12} {'Now':>6}  {'Pred.':>6}  "
          f"{'Grade':<5} Risk")
    print("-" * 70)
    for s in manager.students:
        print(s)
    print("-" * 70)


def predict_screen(manager):
    roll = input("Enter roll number: ").strip()
    s = manager.find(roll)
    if s is None:
        print("No student found with that roll number.")
        return
    print(f"\n--- Report for {s.name} (Roll {s.roll}) ---")
    print(f"Student type          : {s.student_type()}")
    print(f"Test marks            : {s.marks}")
    print(f"Marks trend           : {s.trend()}")
    print(f"Current score         : {s.current_score()}")
    print(f"Predicted next test   : {s.predict_next_mark()}")
    print(f"Predicted final score : {s.predicted_score()}")
    print(f"Predicted grade       : {s.predicted_grade()}")
    print(f"Risk level            : {s.risk_level()}")
    print("Advice:")
    for tip in s.advice():
        print("  -", tip)


def summary_screen(manager):
    if len(manager.students) == 0:
        print("\nNo students recorded yet.")
        return
    # dictionary: grade -> number of students
    grade_count = {}
    for s in manager.students:
        g = s.predicted_grade()
        grade_count[g] = grade_count.get(g, 0) + 1

    total = 0
    for s in manager.students:
        total += s.predicted_score()
    average = total / len(manager.students)

    # max() with a lambda function
    topper = max(manager.students, key=lambda s: s.predicted_score())

    print("\n--- Class Summary ---")
    print(f"Total students          : {len(manager.students)}")
    print(f"Average predicted score : {average:.2f}")
    print(f"Predicted topper        : {topper.name} ({topper.predicted_score()})")
    print("Predicted grade distribution:")
    for grade in sorted(grade_count):
        print(f"  Grade {grade}: {grade_count[grade]}")


def risk_screen(manager):
    # list comprehension
    at_risk = [s for s in manager.students if s.risk_level() == "HIGH"]
    if len(at_risk) == 0:
        print("\nGood news! No student is at high risk.")
        return
    print("\n--- Students at HIGH risk ---")
    for s in at_risk:
        print(f"{s.roll} - {s.name} (predicted score {s.predicted_score()}, "
              f"needs {s.required_score()}+)")


def delete_screen(manager):
    roll = input("Enter roll number to delete: ").strip()
    if manager.delete_student(roll):
        print("Student deleted.")
    else:
        print("No student found with that roll number.")


# ---------------------------------------------------------------
# Main program
# ---------------------------------------------------------------
def main():
    manager = StudentManager()
    print("Welcome to the Student Performance Prediction System!")

    while True:
        show_menu()
        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            add_student_screen(manager)
        elif choice == "2":
            view_all_screen(manager)
        elif choice == "3":
            predict_screen(manager)
        elif choice == "4":
            summary_screen(manager)
        elif choice == "5":
            risk_screen(manager)
        elif choice == "6":
            delete_screen(manager)
        elif choice == "7":
            print("Thank you for using the system. Bye!")
            break
        else:
            print("Invalid choice! Please enter a number from 1 to 7.")


if __name__ == "__main__":
    main()
