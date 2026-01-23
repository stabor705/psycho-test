import customtkinter as ctk
from typing import Callable
import urllib.request
from io import BytesIO
from PIL import Image
from ddgs import DDGS


ANSWER_OPTIONS = [
    "Strongly Agree",
    "Agree",
    "Don't Know",
    "Disagree",
    "Strongly Disagree"
]


class WelcomeFrame(ctk.CTkFrame):
    def __init__(self, parent, on_start: Callable, on_settings: Callable):
        super().__init__(parent, fg_color="transparent")
        self.on_start = on_start
        self.on_settings = on_settings
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        settings_btn = ctk.CTkButton(
            self,
            text="⚙",
            width=40,
            height=40,
            corner_radius=20,
            font=ctk.CTkFont(size=18),
            fg_color="transparent",
            hover_color=("gray75", "gray25"),
            text_color=("gray40", "gray60"),
            command=self.on_settings
        )
        settings_btn.place(relx=1.0, rely=0, anchor="ne", x=-10, y=10)

        title = ctk.CTkLabel(
            self,
            text="Fictional Character Quiz",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title.grid(row=1, column=0, pady=(0, 20))

        subtitle = ctk.CTkLabel(
            self,
            text="Answer personality questions to find\nyour matching character!",
            font=ctk.CTkFont(size=16),
            text_color=("gray40", "gray60")
        )
        subtitle.grid(row=2, column=0, pady=(0, 30))

        start_btn = ctk.CTkButton(
            self,
            text="Start Quiz",
            command=self.on_start,
            width=200,
            height=50,
            corner_radius=25,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        start_btn.grid(row=3, column=0)


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, current_count: int, on_save: Callable, on_cancel: Callable):
        super().__init__(parent, fg_color="transparent")
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.question_count = ctk.IntVar(value=current_count)
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        title = ctk.CTkLabel(
            self,
            text="⚙ Settings",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.grid(row=1, column=0, pady=(0, 40))

        count_label = ctk.CTkLabel(
            self,
            text="Number of Questions",
            font=ctk.CTkFont(size=16)
        )
        count_label.grid(row=2, column=0, pady=(0, 10))

        slider_frame = ctk.CTkFrame(self, fg_color="transparent")
        slider_frame.grid(row=3, column=0, pady=(0, 10))

        self.count_display = ctk.CTkLabel(
            slider_frame,
            text=str(self.question_count.get()),
            font=ctk.CTkFont(size=24, weight="bold"),
            width=50
        )
        self.count_display.pack(side="left", padx=(0, 20))

        self.slider = ctk.CTkSlider(
            slider_frame,
            from_=5,
            to=30,
            number_of_steps=25,
            variable=self.question_count,
            width=300,
            command=self.update_count_display
        )
        self.slider.pack(side="left")

        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=4, column=0, pady=40)

        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            command=self.on_cancel,
            width=120,
            height=40,
            corner_radius=20,
            fg_color="transparent",
            border_width=2,
            text_color=("gray20", "gray80"),
            hover_color=("gray75", "gray25")
        )
        cancel_btn.pack(side="left", padx=10)

        save_btn = ctk.CTkButton(
            buttons_frame,
            text="Save",
            command=lambda: self.on_save(self.question_count.get()),
            width=120,
            height=40,
            corner_radius=20
        )
        save_btn.pack(side="left", padx=10)

    def update_count_display(self, value):
        self.count_display.configure(text=str(int(value)))


class QuizFrame(ctk.CTkFrame):
    def __init__(self, parent, questions: list, statements: dict, on_complete: Callable):
        super().__init__(parent, fg_color="transparent")
        self.questions = questions
        self.statements = statements
        self.on_complete = on_complete
        self.current_index = 0
        self.answers = {}
        self.selected_answer = ctk.StringVar()
        self.create_widgets()
        self.show_question()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(20, 0), padx=40)
        header_frame.grid_columnconfigure(0, weight=1)

        self.progress_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        )
        self.progress_label.grid(row=0, column=0)

        self.progress_bar = ctk.CTkProgressBar(header_frame, width=400, height=8)
        self.progress_bar.grid(row=1, column=0, pady=(10, 0))
        self.progress_bar.set(0)

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        self.question_label = ctk.CTkLabel(
            content_frame,
            text="",
            font=ctk.CTkFont(size=18),
            wraplength=550,
            justify="center"
        )
        self.question_label.grid(row=0, column=0, sticky="s", pady=(0, 30))

        answers_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        answers_frame.grid(row=1, column=0, sticky="n")

        self.radio_buttons = []
        for option in ANSWER_OPTIONS:
            rb = ctk.CTkRadioButton(
                answers_frame,
                text=option,
                value=option,
                variable=self.selected_answer,
                font=ctk.CTkFont(size=14),
                radiobutton_width=22,
                radiobutton_height=22
            )
            rb.pack(anchor="w", pady=8)
            self.radio_buttons.append(rb)

        self.next_btn = ctk.CTkButton(
            self,
            text="Next →",
            command=self.next_question,
            width=160,
            height=45,
            corner_radius=22,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.next_btn.grid(row=2, column=0, pady=30)

    def show_question(self):
        question_id = self.questions[self.current_index]
        question_text = self.statements[question_id]

        progress = (self.current_index + 1) / len(self.questions)
        self.progress_bar.set(progress)
        self.progress_label.configure(
            text=f"Question {self.current_index + 1} of {len(self.questions)}"
        )
        self.question_label.configure(text=question_text)
        self.selected_answer.set("")

        if self.current_index == len(self.questions) - 1:
            self.next_btn.configure(text="Finish ✓")

    def next_question(self):
        if not self.selected_answer.get():
            return

        question_id = self.questions[self.current_index]
        self.answers[question_id] = self.selected_answer.get()
        self.current_index += 1

        if self.current_index >= len(self.questions):
            self.on_complete(self.answers)
        else:
            self.show_question()


class ResultFrame(ctk.CTkFrame):
    def __init__(self, parent, character: str, work: str, similarity: float, on_restart: Callable):
        super().__init__(parent, fg_color="transparent")
        self.on_restart = on_restart
        self.create_widgets(character, work, similarity)

    def fetch_character_image(self, character: str, work: str) -> tuple[ctk.CTkImage, tuple[int, int]] | None:
        try:
            query = f"{character} from {work}"
            with DDGS() as ddgs:
                results = list(ddgs.images(query, max_results=1))
                if results:
                    image_url = results[0]["image"]
                    req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=5) as response:
                        img_data = BytesIO(response.read())
                        img = Image.open(img_data)
                        max_size = 250
                        ratio = min(max_size / img.width, max_size / img.height)
                        new_size = (int(img.width * ratio), int(img.height * ratio))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                        return ctk.CTkImage(light_image=img, dark_image=img, size=new_size), new_size
        except Exception:
            pass
        return None

    def create_widgets(self, character: str, work: str, similarity: float):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        result_card = ctk.CTkFrame(self, corner_radius=20)
        result_card.grid(row=1, column=0, padx=40, pady=20)

        title = ctk.CTkLabel(
            result_card,
            text="Your Matching Character",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(30, 20))

        char_image_result = self.fetch_character_image(character, work)
        if char_image_result:
            char_image, img_size = char_image_result
            image_label = ctk.CTkLabel(result_card, image=char_image, text="")
            image_label.pack(pady=(0, 15))

        character_label = ctk.CTkLabel(
            result_card,
            text=character,
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=("#1a73e8", "#4da6ff")
        )
        character_label.pack(pady=10)

        work_label = ctk.CTkLabel(
            result_card,
            text=f"from \"{work}\"",
            font=ctk.CTkFont(size=16, slant="italic"),
            text_color=("gray40", "gray60")
        )
        work_label.pack(pady=(0, 10))

        similarity_pct = int(similarity * 100)
        similarity_frame = ctk.CTkFrame(result_card, fg_color="transparent")
        similarity_frame.pack(pady=20)

        ctk.CTkLabel(
            similarity_frame,
            text="Similarity",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        ).pack()

        ctk.CTkLabel(
            similarity_frame,
            text=f"{similarity_pct}%",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack()

        sim_bar = ctk.CTkProgressBar(result_card, width=250, height=12)
        sim_bar.pack(pady=(0, 30))
        sim_bar.set(similarity)

        restart_btn = ctk.CTkButton(
            self,
            text="Take Quiz Again",
            command=self.on_restart,
            width=180,
            height=45,
            corner_radius=22,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        restart_btn.grid(row=2, column=0, pady=20)
