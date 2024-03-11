import tkinter as tk
from tkinter import messagebox
from datetime import timedelta
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from faker import Faker
import json
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from concurrent.futures import ProcessPoolExecutor
from check_eng import CheckResult 
from lock_screen import LockScreen
import keyboard
import pyautogui
import pygetwindow as gw
                    
class IELTSWritingApp:
    def __init__(self, master, task_type, chart_type):
        self.master = master
        self.master.title("IELTS Writing Test")
        
        # Set full-screen mode
        self.master.attributes('-fullscreen', True)
        
        self.lock_screen = LockScreen(self.master)
        self.is_locked = False

        # Thời gian làm bài (60 phút)
        self.total_time = timedelta(minutes=60)
        self.remaining_time = self.total_time

        # Tạo label đồng hồ
        self.clock_label = tk.Label(master, text=self.format_time(self.remaining_time), font=("Helvetica", 16))
        self.clock_label.pack()

        # Tạo ô text box chứa đề thi
        self.question_textbox = tk.Text(master, height=5, width=160)
        self.question_textbox.pack()

        self.show_chart_button = tk.Button(master, text="Show Chart", command=self.show_chart)
        self.show_chart_button.pack()

        # Tạo biểu đồ mẫu (có thể thay thế với dữ liệu thực tế)
        self.sample_data = self.generate_random_chart_data(chart_type)

        # Tạo subplot để vẽ biểu đồ
        self.fig, self.ax = plt.subplots()

        # Hiển thị biểu đồ mẫu ban đầu
        self.plot_sample_chart(chart_type, self.sample_data)
        
         # Hiển thị hoặc ẩn biểu đồ dựa trên task_type
        if task_type == 'general':
            self.canvas_widget.pack_forget()  # Ẩn biểu đồ nếu task_type là 'general'
            self.show_chart_button.pack_forget()

        # Tạo ô viết cho từng task
        self.task_textboxes = []
        for task_number in range(1, 3):
            task_label = tk.Label(master, text=f"Task {task_number}:")
            task_label.pack()

            task_textbox = tk.Text(master, height=10, width=80)
            task_textbox.bind("<KeyRelease>", lambda event, task=task_textbox: self.update_word_count(task))
            self.task_textboxes.append(task_textbox)
            task_textbox.pack()

            # Thêm biến để lưu trữ số từ trong mỗi ô viết
            task_textbox.word_count = tk.StringVar()
            word_count_label = tk.Label(master, textvariable=task_textbox.word_count)
            word_count_label.pack()

        # Tạo nút bắt đầu làm bài
        self.start_button = tk.Button(master, text="Start Test", command=self.start_test)
        self.start_button.pack()
        
         # Create a Submit button
        self.submit_button = tk.Button(master, text="Submit", command=self.submit_answers)
        self.submit_button.pack_forget()
        # self.scorer = IELTSScorer()
        
        self.academic_topics = self.read_topics_from_json('database\\topic_test.json')
        
        self.letters = self.read_letters_from_json('database\\topic_test.json')
        self.checker = CheckResult()

        # Cập nhật nội dung đề thi trên từng ô textbox
        self.update_question_textbox(task_type)

    def format_time(self, time_delta):
        minutes, seconds = divmod(time_delta.seconds, 60)
        return "{:02}:{:02}".format(minutes, seconds)

    def submit_answers(self):
        # Check if time is up
        if self.remaining_time <= timedelta(0):
            messagebox.showinfo("Time's up!", "Your time is up. The test will be submitted.")
            self.lock_screen = LockScreen(self.master)
            self.lock_screen.show()

        # If time is not up, check word count for each task
        for idx, task_textbox in enumerate(self.task_textboxes, start=1):
            word_count = len(task_textbox.get("1.0", tk.END).split())
            if idx == 1 and word_count < 150:
                messagebox.showinfo("Word Count Warning", "Task 1 should have a minimum of 150 words.")
                return  # Return to let the user continue working
            if idx == 2 and word_count < 250:
                messagebox.showinfo("Word Count Warning", "Task 2 should have a minimum of 250 words.")
                return  # Return to let the user continue working

        # All conditions are met, confirm submission
        confirm_submission = messagebox.askyesno("Confirm Submission", "Do you want to submit the test?")
        if confirm_submission:
            messagebox.showinfo("Submission", "Test submitted successfully. Locking the screen.")
            self.master.withdraw()  # Hide the main window

            # Create and show the lock screen
            self.lock_screen = LockScreen(self.master)
            self.lock_screen.show()

            # Perform additional checks using CheckResult class
            self.check_results() 
        else:
            messagebox.showinfo("Continue", "Continue working on your test.")
            
    def update_clock(self):
        if self.remaining_time > timedelta(0):
            self.remaining_time -= timedelta(seconds=1)
            self.clock_label.config(text=self.format_time(self.remaining_time))
            self.master.after(1000, self.update_clock)
        else:
            messagebox.showinfo("Time's up!", "Your time is up. Please submit your answers.")
            self.submit_answers()

    def generate_random_chart_data(self, chart_type, chart_data=None):
        fake = Faker()

        if chart_type == 'line':
            categories = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
            values = [random.randint(20, 50) for _ in range(len(categories))]
            return dict(zip(categories, values))

        elif chart_type == 'bar':
            categories = ["Category A", "Category B", "Category C", "Category D"]
            values = [random.randint(20, 50) for _ in range(len(categories))]
            return dict(zip(categories, values))

        elif chart_type == 'pie':
            labels = ["Label 1", "Label 2", "Label 3", "Label 4"]
            sizes = [random.randint(5, 30) for _ in range(len(labels))]
            return dict(zip(labels, sizes))

        elif chart_type == 'table':
            data = {
                'Category': ["A", "B", "C", "D"],
                'Value 1': [random.randint(20, 50) for _ in range(4)],
                'Value 2': [random.randint(20, 50) for _ in range(4)],
            }
            return data
               
        elif chart_type == 'process':
            # Handle the case where chart_data is None
            if chart_data is None:
                return {'steps': [], 'connections': []}

            steps = chart_data['steps']
            connections = chart_data['connections']

            # Create positions for each step
            node_positions = {step: (i, 0) for i, step in enumerate(steps)}

            # Plot connections
            for connection in connections:
                start_position = node_positions[connection['start']]
                end_position = node_positions[connection['end']]
                self.ax.arrow(start_position[0], start_position[1], end_position[0] - start_position[0], end_position[1] - start_position[1],
                        head_width=0.05, head_length=0.1, fc='blue', ec='blue')

            # Plot steps
            for step, position in node_positions.items():
                self.ax.text(position[0], position[1], step, ha='center', va='center', bbox=dict(facecolor='white', edgecolor='black'))
                # Hide axes
                self.ax.axis('off')
        
        elif chart_type =='combination-chart':
             # Assuming you have both bar and line data
            categories = ["Category A", "Category B", "Category C", "Category D"]
            bar_values = [random.randint(20, 50) for _ in range(len(categories))]
            line_values = [random.randint(30, 60) for _ in range(len(categories))]

            return {
                'categories': categories,
                'bar': bar_values,
                'line': line_values
            }
        
        elif chart_type == 'map':
            map_data = {
                'buildings': ["Building 1", "Building 2", "Building 3", "Building 4"],
                'positions': [(random.randint(0, 10), random.randint(0, 10)) for _ in range(4)]
            }
            return map_data
        
        else:
            raise ValueError("Invalid chart type")
        
    def plot_sample_chart(self, chart_type, chart_data):
        if chart_type == 'line':
            self.ax.plot(list(chart_data.keys()), list(chart_data.values()))
            self.ax.set_xlabel("Categories")
            self.ax.set_ylabel("Values")
            self.ax.set_title("Line Graph")

        elif chart_type == 'bar':
            self.ax.bar(list(chart_data.keys()), list(chart_data.values()))
            self.ax.set_xlabel("Categories")
            self.ax.set_ylabel("Values")
            self.ax.set_title("Bar Graph")

        elif chart_type == 'pie':
            self.ax.pie(list(chart_data.values()), labels=list(chart_data.keys()), autopct='%1.1f%%')
            self.ax.set_title("Pie Chart")

        elif chart_type == 'table':
            table_data = [list(chart_data.keys())] + [list(map(str, row)) for row in zip(*chart_data.values())]
            self.ax.axis('off')
            self.ax.table(cellText=table_data, loc='center', cellLoc='center', colLabels=None)

        elif chart_type == 'process':
            data = self.load_process_data()

            production_steps = data.get('production_steps', [])
            production_connections = data.get('production_connections', [])

            # Assign positions to each step
            node_positions = {step: (i, 0) for i, step in enumerate(production_steps)}

            # Plot connections
            for connection in production_connections:
                start_position = node_positions[connection['start']]
                end_position = node_positions[connection['end']]
                self.ax.arrow(start_position[0], start_position[1], end_position[0] - start_position[0], end_position[1] - start_position[1],
                        head_width=0.05, head_length=0.1, fc='blue', ec='blue')

            # Plot steps
            for step, position in node_positions.items():
                self.ax.text(position[0], position[1], step, ha='center', va='center', bbox=dict(facecolor='white', edgecolor='black'))
                # Hide axes
                self.ax.axis('off')
                
        elif chart_type == 'combination-chart':
            # Assuming chart_data contains both bar and line data
            categories = chart_data['categories']
            bar_values = chart_data['bar']
            line_values = chart_data['line']

            # Bar chart
            self.ax.bar(categories, bar_values, label='Bar Chart')

            # Line chart
            self.ax.plot(categories, line_values, marker='o', linestyle='-', color='r', label='Line Chart')

        elif chart_type == 'map':
            for building, position in zip(chart_data['buildings'], chart_data['positions']):
                # Draw a rectangle for the building
                rect = patches.Rectangle(position, 1, 1, linewidth=1, edgecolor='r', facecolor='none')
                self.ax.add_patch(rect)

                # Label the building
                plt.text(position[0] + 0.5, position[1] + 0.5, building, ha='center', va='center')

            self.ax.set_title("Map Diagram")
            plt.xlim(0, 15)
            plt.ylim(0, 15)
            self.ax.axis('off')
            
        else:
            raise ValueError("Invalid chart type")

        # Hiển thị biểu đồ trong Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack_forget()

    def show_chart(self):
        # Hiển thị hoặc ẩn biểu đồ khi nút "Show Chart" được nhấn
        if self.show_chart_button["text"] == "Show Chart":
            self.show_chart_button.config(text="Hide Chart")
            self.canvas_widget.pack()
        else:
            self.show_chart_button.config(text="Show Chart")
            self.canvas_widget.pack_forget()

    def start_test(self):
        # Bắt đầu đồng hồ đếm ngược
        self.start_button.config(state=tk.DISABLED)
        self.update_clock()

        # Display the submit_button
        self.submit_button.pack()
        
        self.start_button.pack_forget()
        
        self.lock_screen.lock_window()
        
        keyboard.hook(self.lock_screen.on_key_event)
            
    def update_word_count(self, task_textbox):
        # Đếm số từ và cập nhật biến word_count
        word_count = len(task_textbox.get("1.0", tk.END).split())
        task_textbox.word_count.set(f"Word Count: {word_count}")

    def update_question_textbox(self, task_type):
        # Cập nhật nội dung đề thi trên từng ô textbox
        if task_type == 'academic':
            # Hiển thị chart nếu là academic
            task_1_content = self.generate_random_task(task_type, task_number=1)
        elif task_type == 'general':
            # Hiển thị letters nếu là general
            task_1_content = self.generate_random_task(task_type, task_number=1, letters=self.read_letters_from_json())

        task_2_content = self.generate_random_task(task_type, task_number=2, topics=self.academic_topics)
        question_content = f"IELTS Writing Test Question\nTask 1 ({task_type}):\n{task_1_content}\n\nTask 2 ({task_type}):\n{task_2_content}"
        self.question_textbox.delete(1.0, tk.END)  # Xóa nội dung cũ trước khi thêm nội dung mới
        self.question_textbox.insert(tk.END, question_content)
        
    def generate_random_task(self, task_type, task_number, topics=None, letters=None):
        fake = Faker()

        if task_type == 'academic':
            academic_task_types = [
                "Graph or Chart Description: You might be presented with a graph, chart, table, or diagram. Your task is to describe and interpret the information in a report format.",
                "Process Description: You might need to explain a process or sequence of events illustrated in a diagram."
            ]

            if task_number == 1:
                return fake.random_element(academic_task_types)
            elif task_number == 2:
                if topics is not None and isinstance(topics, list) and len(topics) > 0:
                    return f"Essay Writing: You will be given the topic: \n '{fake.random_element(topics)}' \n and asked to present an argument, analyze a problem, or express your opinion. The essay should be well-organized and coherent."

        elif task_type == 'general':
            if task_number == 1 and letters is not None and isinstance(letters, list) and len(letters) > 0:
                selected_letter = fake.random_element(letters)
                return f"You should spend about 20 minutes on this task. \n Letter Writing: You will be asked to write a letter. This could be a formal, semi-formal, or informal letter, depending on the context. \n '{selected_letter}'\n"
            elif task_number == 2:
                if topics is not None and isinstance(topics, list) and len(topics) > 0:
                    return f"Essay Writing: You will be given the topic: \n '{fake.random_element(topics)}' \n and asked to present an argument, analyze a problem, or express your opinion. The essay should be well-organized and coherent."
        
        raise ValueError("Invalid task type or task number")

    @staticmethod
    def read_topics_from_json(file_path='database\\topic_test.json'):
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get('topics', [])
        
    @staticmethod
    def read_letters_from_json(file_path='database\\topic_test.json'):
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data.get('letters', [])

    def load_process_data(self, file_path='database\\topic_test.json'):
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            return data.get('data', {})

    def check_results(self):
        # Perform additional checks using the CheckResult class
        # Example: Call check_writing and check_grammar
        text_to_check = self.task_textboxes[0].get("1.0", tk.END)  # You may adjust this based on your needs
        avoid_writing_results = self.checker.check_writing(text_to_check)
        grammar_results, _ = self.checker.check_grammar(text_to_check)

        # Process the results as needed
        print("Avoid Writing Results:", avoid_writing_results)
        print("Grammar Results:", grammar_results)

        # After processing, unlock the screen
        self.unlock_screen()

    def unlock_screen(self):
        if self.lock_screen:
            self.lock_screen.hide()  # Hide the lock screen
            self.master.deiconify()  # Show the main window again

if __name__ == "__main__":
    root = tk.Tk()

    # Chọn ngẫu nhiên giữa 'academic' và 'general'
    task_type = random.choice(['academic', 'general'])
    chart_type = random.choice (['line', 'bar', 'pie', 'table', 'process','combination-chart'])
    app = IELTSWritingApp(root, task_type= task_type, chart_type= chart_type)

    root.mainloop()