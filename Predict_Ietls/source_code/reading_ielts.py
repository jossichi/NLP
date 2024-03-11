import tkinter as tk
from tkinter import messagebox
from datetime import timedelta
import json
import random

class ReadingTestApp:
    def __init__(self, master, question_type):
        self.master = master
        self.master.title("IELTS Reading Test")

        # Thời gian làm bài (60 phút)
        self.total_time = timedelta(minutes=60)
        self.remaining_time = self.total_time

        self.clock_label = tk.Label(master, text=self.format_time(self.remaining_time), font=("Helvetica", 16))
        self.clock_label.pack()

        self.passage_label = tk.Text(master, height=10, width=160)
        self.passage_label.pack()

        self.start_button = tk.Button(master, text="Start Test", command=self.start_test)
        self.start_button.pack()

        # Create Next and Previous buttons
        self.next_button = tk.Button(master, text="Next", command=self.display_next_question)
        self.next_button.pack_forget()

        self.prev_button = tk.Button(master, text="Previous", command=self.display_prev_question)
        self.prev_button.pack_forget()

        # Create a Submit button
        self.submit_button = tk.Button(master, text="Submit", command=self.submit_test)
        self.submit_button.pack_forget()

        self.sections = self.generate_sections(question_type)
        self.current_section_index = 0
        self.current_question_index = 0
        self.user_answers = {}

        self.load_section()

        self.master.attributes('-fullscreen', True)

    def generate_sections(self, question_type):
        if question_type == 'academic':
            sections_data = self.read_academic_sections()
        elif question_type == 'general':
            sections_data = self.read_general_sections()
        else:
            raise ValueError("Invalid question type")

        if isinstance(sections_data, list):
            # Assume sections_data is already a list of sections
            result_sections = sections_data
        elif isinstance(sections_data, dict):
            # Assume sections_data is a dictionary
            result_sections = sections_data.get(question_type, [])
        else:
            # Assume sections_data is a JSON string, so parse it
            data = json.loads(sections_data)
            result_sections = data.get(question_type, [])

        formatted_sections = []
        for section_data in result_sections:
            section_type = section_data.get('type', 'multiple_choice')
            if section_type == 'multiple_choice':
                formatted_sections.append({
                    'passage': section_data['passage'],
                    'content': section_data['content'],
                    'questions': section_data.get('questions', []),
                    'type': 'multiple_choice'
                })
            elif section_type == 'fill_in_the_blanks':
                formatted_sections.append({
                    'passage': section_data['passage'],
                    'content': section_data['content'],
                    'fill_in_the_blanks': section_data.get('fill_in_the_blanks', {}),
                    'type': 'fill_in_the_blanks'
                })

        if not formatted_sections:
            print(f"No sections found for the specified question type: {question_type}")
            raise ValueError("No sections found for the specified question type")

        random.shuffle(formatted_sections)
        return formatted_sections

    def load_section(self):
        current_section = self.sections[self.current_section_index]

        passage_content = f"{current_section['passage']}\n\n{current_section['content']}\n\n"
        self.passage_label.delete(1.0, tk.END)
        self.passage_label.insert(tk.END, passage_content)

        self.user_answers[self.current_section_index + 1] = tk.StringVar()

        if current_section['type'] == 'multiple_choice' and current_section['questions']:
            self.display_multiple_choice_question(current_section)
        elif current_section['type'] == 'fill_in_the_blanks':
            self.display_fill_in_the_blanks_section(current_section)

    def display_multiple_choice_question(self, section):
        for i, question_data in enumerate(section['questions']):
            question_content = question_data["question"]
            options = question_data.get("options", [])
            correct_answer = question_data.get("correct_answer")

            if options and correct_answer:
                tk.Label(self.master, text=question_content).pack()
                for option in options:
                    tk.Radiobutton(self.master, text=option, variable=self.user_answers[self.current_section_index + 1], value=option).pack()

    def display_fill_in_the_blanks_section(self, section):
        blanks = section['fill_in_the_blanks'].get('blanks', [])
        if blanks:
            tk.Label(self.master, text="Fill in the blanks:").pack()
            for blank in blanks:
                tk.Label(self.master, text=blank).pack()
                entry = tk.Entry(self.master, textvariable=self.user_answers[self.current_section_index + 1])
                entry.pack()

    def format_time(self, time_delta):
        minutes, seconds = divmod(time_delta.seconds, 60)
        return "{:02}:{:02}".format(minutes, seconds)

    def start_test(self):
        # Bắt đầu đồng hồ đếm ngược
        self.start_button.config(state=tk.DISABLED)
        self.next_button.pack()
        self.prev_button.pack()
        self.update_timer()

        # Display the submit_button
        self.submit_button.pack()

        self.start_button.pack_forget()

    def update_timer(self):
        if self.remaining_time > timedelta(0):
            self.remaining_time -= timedelta(seconds=1)
            self.clock_label.config(text=self.format_time(self.remaining_time))
            self.master.after(1000, self.update_timer)
        else:
            messagebox.showinfo("Time's up!", "Your time is up. Please submit your answers.")
            self.submit_test()

    def submit_test(self):
        # Kiểm tra xem có câu nào trống không
        unanswered_sections = [i + 1 for i, section in enumerate(self.sections) if not self.get_user_answer(i + 1)]
        if unanswered_sections:
            messagebox.showinfo("OK", f"Section {', '.join(map(str, unanswered_sections))} chưa được trả lời.")
        else:
            result = self.check_answers()
            messagebox.showinfo("Kết quả", f"Điểm số của bạn: {result}")

    def check_answers(self):
        # Kiểm tra câu trả lời và tính điểm
        correct_answers = 0
        for i, section in enumerate(self.sections):
            user_answer = self.get_user_answer(i + 1)
            if user_answer and user_answer == section.get('correct_answer', section.get('answer')):
                correct_answers += 1
        return correct_answers

    def get_user_answer(self, section_number):
        user_answer = self.user_answers.get(section_number)
        return user_answer.get() if user_answer else None

    def display_next_question(self):
        self.current_section_index += 1
        if self.current_section_index < len(self.sections):
            self.load_section()
        else:
            # Display a message or take appropriate action as the last question is reached
            messagebox.showinfo("End of Test", "You have reached the end of the test.")
            self.current_section_index -= 1

    def display_prev_question(self):
        self.current_section_index -= 1
        if self.current_section_index >= 0:
            self.load_section()
        else:
            # Display a message or take appropriate action as the first question is reached
            messagebox.showinfo("Start of Test", "This is the first question.")
            self.current_section_index += 1

    @staticmethod
    def read_general_sections(file_path='database\\reading.json'):
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get('general', [])

    @staticmethod
    def read_academic_sections(file_path='database\\reading.json'):
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get('academic', [])

if __name__ == "__main__":
    root = tk.Tk()
    app = ReadingTestApp(root, question_type='academic')  # Replace 'academic' with 'general' if needed
    root.mainloop()
