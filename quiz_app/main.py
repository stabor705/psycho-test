import customtkinter as ctk

from quiz_app.quiz_logic import (
    load_statements,
    load_character_works,
    get_random_questions,
    find_matching_character
)
from quiz_app.gui import WelcomeFrame, SettingsFrame, QuizFrame, ResultFrame


class QuizApp:
    def __init__(self):
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Fictional Character Quiz")
        self.root.geometry("900x750")
        self.root.minsize(800, 650)

        self.statements = load_statements()
        self.character_works = load_character_works()
        self.question_count = 10
        self.current_frame = None
        self.show_welcome()

    def clear_frame(self):
        if self.current_frame:
            self.current_frame.destroy()

    def show_welcome(self):
        self.clear_frame()
        self.current_frame = WelcomeFrame(self.root, self.start_quiz, self.show_settings)
        self.current_frame.pack(fill="both", expand=True)

    def show_settings(self):
        self.clear_frame()
        self.current_frame = SettingsFrame(
            self.root,
            self.question_count,
            self.save_settings,
            self.show_welcome
        )
        self.current_frame.pack(fill="both", expand=True)

    def save_settings(self, count: int):
        self.question_count = count
        self.show_welcome()

    def start_quiz(self):
        self.clear_frame()
        questions = get_random_questions(self.statements, self.question_count)
        self.current_frame = QuizFrame(
            self.root,
            questions,
            self.statements,
            self.show_result
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_result(self, answers: dict):
        self.clear_frame()
        character, similarity = find_matching_character(answers)
        work = self.character_works.get(character, "Unknown")
        self.current_frame = ResultFrame(
            self.root,
            character,
            work,
            similarity,
            self.show_welcome
        )
        self.current_frame.pack(fill="both", expand=True)

    def run(self):
        self.root.mainloop()


def main():
    app = QuizApp()
    app.run()


if __name__ == "__main__":
    main()
