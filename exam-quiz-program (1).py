import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
import json
from typing import List, Dict
import random
from datetime import datetime
import os

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Examen Quiz Programma")
        self.geometry("800x600")
        self.questions: List[Dict] = []
        self.current_question = 0
        self.score = 0
        self.user_answers = []
        self.quiz_history = []
        self.load_history()
        self.create_widgets()

    def create_widgets(self):
        # Main menu frame
        self.file_frame = tk.Frame(self)
        self.file_frame.pack(pady=20)

        self.file_button = tk.Button(self.file_frame, text="Selecteer CSV Bestand", command=self.load_file)
        self.file_button.pack()

        self.history_button = tk.Button(self.file_frame, text="Bekijk Geschiedenis", command=self.show_history)
        self.history_button.pack(pady=10)

        # Question frame
        self.question_frame = tk.Frame(self)
        self.question_label = tk.Label(self.question_frame, text="", wraplength=700, justify="center")
        self.question_label.pack(pady=20)

        self.answer_var = tk.StringVar()
        self.answer_buttons = []
        for i in range(4):
            button = tk.Radiobutton(self.question_frame, text="", variable=self.answer_var, value=str(i), wraplength=600, justify="left")
            button.pack(anchor="w", padx=50, pady=5)
            self.answer_buttons.append(button)

        self.submit_button = tk.Button(self.question_frame, text="Bevestig Antwoord", command=self.check_answer)
        self.submit_button.pack(pady=20)

        # Result label
        self.result_label = tk.Label(self.question_frame, text="")
        self.result_label.pack()

        # Stats frame
        self.stats_frame = tk.Frame(self)
        self.stats_label = tk.Label(self.stats_frame, text="")
        self.stats_label.pack()

        self.review_button = tk.Button(self.stats_frame, text="Bekijk Antwoorden", command=self.show_review)
        self.review_button.pack(pady=10)

        self.new_quiz_button = tk.Button(self.stats_frame, text="Nieuwe Quiz", command=self.reset_quiz)
        self.new_quiz_button.pack(pady=10)

        # Review frame
        self.review_frame = tk.Frame(self)
        self.review_canvas = tk.Canvas(self.review_frame)
        self.review_scrollbar = ttk.Scrollbar(self.review_frame, orient="vertical", command=self.review_canvas.yview)
        self.review_scrollable_frame = tk.Frame(self.review_canvas)

        self.review_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.review_canvas.configure(
                scrollregion=self.review_canvas.bbox("all")
            )
        )

        self.review_canvas.create_window((0, 0), window=self.review_scrollable_frame, anchor="nw")
        self.review_canvas.configure(yscrollcommand=self.review_scrollbar.set)

        self.review_canvas.pack(side="left", fill="both", expand=True)
        self.review_scrollbar.pack(side="right", fill="y")

        # History frame
        self.history_frame = tk.Frame(self)
        self.history_listbox = tk.Listbox(self.history_frame, width=70)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_scrollbar = ttk.Scrollbar(self.history_frame, orient="vertical", command=self.history_listbox.yview)
        self.history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox.config(yscrollcommand=self.history_scrollbar.set)

        self.history_back_button = tk.Button(self.history_frame, text="Terug naar Hoofdmenu", command=self.back_to_main)
        self.history_back_button.pack(pady=10)

    def load_history(self):
        if os.path.exists('quiz_history.json'):
            with open('quiz_history.json', 'r') as f:
                self.quiz_history = json.load(f)

    def save_history(self):
        with open('quiz_history.json', 'w') as f:
            json.dump(self.quiz_history, f)

    def show_history(self):
        self.file_frame.pack_forget()
        self.history_frame.pack(fill=tk.BOTH, expand=True)
        self.history_listbox.delete(0, tk.END)
        for quiz in self.quiz_history:
            self.history_listbox.insert(tk.END, f"Datum: {quiz['date']}, Score: {quiz['score']}/{quiz['total']}, Percentage: {quiz['percentage']:.2f}%")

    def back_to_main(self):
        self.history_frame.pack_forget()
        self.file_frame.pack(pady=20)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Bestanden", "*.csv")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8-sig') as csvfile:
                    reader = csv.DictReader(csvfile, delimiter=',')
                    expected_columns = {'vraag', 'optie1', 'optie2', 'optie3', 'optie4', 'juiste_antwoord', 'uitleg'}
                    
                    csv_columns = set(reader.fieldnames if reader.fieldnames else [])
                    print("CSV-kolommen gevonden:", csv_columns)
                    
                    missing_columns = expected_columns - csv_columns
                    if missing_columns:
                        messagebox.showerror("Fout", f"Het bestand mist de volgende kolommen: {', '.join(missing_columns)}")
                        return

                    self.questions = [{
                        'vraag': row['vraag'],
                        'opties': [row['optie1'], row['optie2'], row['optie3'], row['optie4']],
                        'juiste_antwoord': row['juiste_antwoord'],
                        'uitleg': row['uitleg']
                    } for row in reader]

                random.shuffle(self.questions)
                self.start_quiz()

            except Exception as e:
                messagebox.showerror("Fout", f"Fout bij het laden van het bestand: {str(e)}")

    def start_quiz(self):
        self.file_frame.pack_forget()
        self.question_frame.pack(fill=tk.BOTH, expand=True)
        self.current_question = 0
        self.score = 0
        self.user_answers = []
        self.show_question()

    def show_question(self):
        if self.current_question < len(self.questions):
            q = self.questions[self.current_question]
            self.question_label.config(text=q['vraag'])
            options = q['opties'].copy()
            random.shuffle(options)
            for i, option in enumerate(options):
                self.answer_buttons[i].config(text=option)
            self.answer_var.set("")
            self.submit_button.config(state=tk.NORMAL)
            self.result_label.config(text="")
        else:
            self.show_final_results()

    def check_answer(self):
        if not self.answer_var.get():
            messagebox.showwarning("Waarschuwing", "Selecteer alstublieft een antwoord.")
            return

        q = self.questions[self.current_question]
        selected_answer = self.answer_buttons[int(self.answer_var.get())].cget("text")
        correct_answer = q['juiste_antwoord']

        self.user_answers.append(selected_answer)

        if selected_answer == correct_answer:
            self.score += 1
            self.result_label.config(text="Juist!", fg="green")
        else:
            self.result_label.config(text=f"Onjuist. Het juiste antwoord was: {correct_answer}", fg="red")

        self.submit_button.config(state=tk.DISABLED)
        self.after(1500, self.next_question)

    def next_question(self):
        self.current_question += 1
        self.show_question()

    def show_final_results(self):
        self.question_frame.pack_forget()
        self.stats_frame.pack()
        percentage = (self.score / len(self.questions)) * 100
        stats_text = f"Quiz Voltooid!\n\n"
        stats_text += f"Totaal aantal vragen: {len(self.questions)}\n"
        stats_text += f"Juiste antwoorden: {self.score}\n"
        stats_text += f"Onjuiste antwoorden: {len(self.questions) - self.score}\n"
        stats_text += f"Percentage: {percentage:.2f}%\n\n"

        if percentage >= 90:
            stats_text += "Uitstekend werk!"
        elif percentage >= 70:
            stats_text += "Goed gedaan!"
        elif percentage >= 50:
            stats_text += "Niet slecht, maar er is ruimte voor verbetering."
        else:
            stats_text += "Je zou wat meer kunnen studeren en het opnieuw proberen."

        self.stats_label.config(text=stats_text)

        # Save quiz results to history
        self.quiz_history.append({
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'score': self.score,
            'total': len(self.questions),
            'percentage': percentage
        })
        self.save_history()

    def show_review(self):
        self.stats_frame.pack_forget()
        self.review_frame.pack(fill="both", expand=True)

        for widget in self.review_scrollable_frame.winfo_children():
            widget.destroy()

        for i, (q, user_answer) in enumerate(zip(self.questions, self.user_answers), 1):
            question_frame = tk.Frame(self.review_scrollable_frame, relief=tk.RAISED, borderwidth=1)
            question_frame.pack(fill="x", padx=5, pady=5)

            question_label = tk.Label(question_frame, text=f"Vraag {i}: {q['vraag']}", wraplength=700, justify="left", anchor="w")
            question_label.pack(fill="x")

            for j, option in enumerate(q['opties'], 1):
                color = "black"
                if option == q['juiste_antwoord']:
                    color = "green"
                elif option == user_answer and user_answer != q['juiste_antwoord']:
                    color = "red"
                
                option_label = tk.Label(question_frame, text=f"  Optie {j}: {option}", wraplength=680, justify="left", anchor="w", fg=color)
                option_label.pack(fill="x")

            uitleg_label = tk.Label(question_frame, text=f"Uitleg: {q['uitleg']}", wraplength=700, justify="left", anchor="w")
            uitleg_label.pack(fill="x")

        back_button = tk.Button(self.review_scrollable_frame, text="Terug naar Resultaten", command=self.back_to_results)
        back_button.pack(pady=20)

    def back_to_results(self):
        self.review_frame.pack_forget()
        self.stats_frame.pack()

    def reset_quiz(self):
        self.stats_frame.pack_forget()
        self.review_frame.pack_forget()
        self.file_frame.pack(pady=20)
        self.questions.clear()
        self.user_answers.clear()

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()