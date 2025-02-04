import tkinter as tk
from tkinter import messagebox, simpledialog
import calendar
import pandas as pd
from datetime import datetime

class AttendanceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Tracker")
        self.root.geometry("600x400")

        # Initialize data
        self.timetable = {}
        self.holidays = []
        self.attendance = {}  # Format: { "YYYY-MM-DD": { "Subject": "Present/Absent" } }

        # Load saved data (if any)
        self.load_data()

        # If timetable is not set, prompt the user to set it
        if not self.timetable:
            self.set_timetable()

        # Create GUI
        self.create_widgets()

    def create_widgets(self):
        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Set Timetable", command=self.set_timetable)
        file_menu.add_command(label="Add Holiday", command=self.add_holiday)
        file_menu.add_separator()
        file_menu.add_command(label="Save Data", command=self.save_data)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Attendance Menu
        attendance_menu = tk.Menu(menubar, tearoff=0)
        attendance_menu.add_command(label="View Attendance Percentage", command=self.view_attendance_percentage)
        menubar.add_cascade(label="Attendance", menu=attendance_menu)

        # Calendar Frame
        self.calendar_frame = tk.Frame(self.root)
        self.calendar_frame.pack(pady=20)

        # Display Calendar
        self.display_calendar()

    def display_calendar(self):
        # Clear previous calendar
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Get current year and month
        now = datetime.now()
        self.year = now.year
        self.month = now.month

        # Create calendar
        cal = calendar.monthcalendar(self.year, self.month)
        for i, week in enumerate(cal):
            for j, day in enumerate(week):
                if day != 0:
                    day_str = f"{self.year}-{self.month:02d}-{day:02d}"
                    day_name = calendar.day_name[calendar.weekday(self.year, self.month, day)]
                    button = tk.Button(
                        self.calendar_frame,
                        text=str(day),
                        width=5,
                        bg="lightgreen" if day_str not in self.holidays else "lightblue",
                        command=lambda d=day_str, dn=day_name: self.mark_attendance(d, dn),
                    )
                    button.grid(row=i, column=j, padx=5, pady=5)

    def set_timetable(self):
        # Create a new window for timetable entry
        timetable_window = tk.Toplevel(self.root)
        timetable_window.title("Set Timetable")
        timetable_window.geometry("400x300")

        # Days of the week
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Create entry fields for each day
        self.timetable_entries = {}
        for i, day in enumerate(days):
            frame = tk.Frame(timetable_window)
            frame.pack(pady=5)

            label = tk.Label(frame, text=day)
            label.pack(side=tk.LEFT)

            entry = tk.Entry(frame, width=30)
            entry.pack(side=tk.RIGHT)

            # Pre-fill with existing data (if any)
            if day in self.timetable:
                entry.insert(0, ", ".join(self.timetable[day]))

            self.timetable_entries[day] = entry

        # Save button
        save_button = tk.Button(timetable_window, text="Save Timetable", command=self.save_timetable)
        save_button.pack(pady=10)

    def save_timetable(self):
        # Save the timetable from the entry fields
        for day, entry in self.timetable_entries.items():
            subjects = entry.get().strip()
            if subjects:
                self.timetable[day] = [s.strip() for s in subjects.split(",")]
            else:
                self.timetable[day] = []
        messagebox.showinfo("Saved", "Timetable saved successfully!")

    def add_holiday(self):
        # Add a holiday
        holiday = simpledialog.askstring("Add Holiday", "Enter holiday date (YYYY-MM-DD):")
        if holiday:
            self.holidays.append(holiday)
            self.display_calendar()

    def mark_attendance(self, date, day_name):
        # Mark attendance for individual subjects
        if date in self.holidays:
            messagebox.showinfo("Holiday", f"{date} is a holiday!")
            return

        # Get subjects for the day
        subjects = self.timetable.get(day_name, [])
        if not subjects:
            messagebox.showinfo("No Subjects", f"No subjects found for {day_name}.")
            return

        # Create a popup window to mark attendance for each subject
        popup = tk.Toplevel(self.root)
        popup.title(f"Mark Attendance for {date}")
        popup.geometry("300x200")

        # Track attendance for each subject
        attendance_status = {}
        for subject in subjects:
            frame = tk.Frame(popup)
            frame.pack(pady=5)

            label = tk.Label(frame, text=subject)
            label.pack(side=tk.LEFT)

            var = tk.StringVar(value="Present")
            dropdown = tk.OptionMenu(frame, var, "Present", "Absent")
            dropdown.pack(side=tk.RIGHT)

            attendance_status[subject] = var

        # Save button
        save_button = tk.Button(popup, text="Save", command=lambda: self.save_attendance(date, attendance_status, popup))
        save_button.pack(pady=10)

    def save_attendance(self, date, attendance_status, popup):
        # Save attendance for the date
        self.attendance[date] = {subject: var.get() for subject, var in attendance_status.items()}
        messagebox.showinfo("Saved", f"Attendance saved for {date}.")
        popup.destroy()

    def view_attendance_percentage(self):
        # Calculate attendance percentage for each subject
        subject_stats = {}
        for date, subjects in self.attendance.items():
            for subject, status in subjects.items():
                if subject not in subject_stats:
                    subject_stats[subject] = {"Present": 0, "Total": 0}
                subject_stats[subject]["Total"] += 1
                if status == "Present":
                    subject_stats[subject]["Present"] += 1

        # Calculate percentage
        percentage_data = []
        for subject, stats in subject_stats.items():
            total = stats["Total"]
            present = stats["Present"]
            percentage = (present / total) * 100 if total > 0 else 0
            percentage_data.append([subject, f"{percentage:.2f}%"])

        # Display in a new window
        popup = tk.Toplevel(self.root)
        popup.title("Attendance Percentage")
        popup.geometry("300x200")

        # Create a table to display percentages
        for i, (subject, percentage) in enumerate(percentage_data):
            label_subject = tk.Label(popup, text=subject)
            label_subject.grid(row=i, column=0, padx=10, pady=5)

            label_percentage = tk.Label(popup, text=percentage)
            label_percentage.grid(row=i, column=1, padx=10, pady=5)

    def save_data(self):
        # Save data to CSV files
        pd.DataFrame(list(self.timetable.items()), columns=["Day", "Subjects"]).to_csv("timetable.csv", index=False)
        pd.DataFrame(self.holidays, columns=["Holiday"]).to_csv("holidays.csv", index=False)
        attendance_data = []
        for date, subjects in self.attendance.items():
            for subject, status in subjects.items():
                attendance_data.append([date, subject, status])
        pd.DataFrame(attendance_data, columns=["Date", "Subject", "Status"]).to_csv("attendance.csv", index=False)
        messagebox.showinfo("Save", "Data saved successfully!")

    def load_data(self):
        # Load data from CSV files
        try:
            self.timetable = dict(pd.read_csv("timetable.csv").values)
            self.holidays = pd.read_csv("holidays.csv")["Holiday"].tolist()
            attendance_data = pd.read_csv("attendance.csv")
            for _, row in attendance_data.iterrows():
                date = row["Date"]
                subject = row["Subject"]
                status = row["Status"]
                if date not in self.attendance:
                    self.attendance[date] = {}
                self.attendance[date][subject] = status
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceTracker(root)
    root.mainloop()