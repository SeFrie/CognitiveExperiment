import tkinter as tk
import pandas as pd
import os
import random


class TestScreen:
    def __init__(self, root, word_data, unique_id, completion_callback=None):
        """
        Initialize the test screen

        Args:
            root: The tkinter root window
            word_data: DataFrame with word pairs
            unique_id: Unique session identifier
            completion_callback: Function to call when test is completed
        """
        self.root = root
        self.word_data = word_data
        self.unique_id = unique_id
        self.completion_callback = completion_callback

        # Create randomized question order
        self.question_indices = list(range(len(self.word_data)))
        random.shuffle(self.question_indices)  # Randomize the order

        # Initialize test variables
        self.current_question = 0
        self.answers = {}  # Store answers by word_id (not question index)
        self.total_questions = min(25, len(self.word_data))  # Changed from 20 to 25

        # Timer variables
        self.time_remaining = 3 * 60  # 3 minutes in seconds
        self.timer_display = None

        # UI components
        self.question_cards = []
        self.card_frames = []  # Store the border frames
        self.question_label = None
        self.answer_entry = None
        self.prev_button = None
        self.next_button = None

        print(f"First test created with randomized order: {self.question_indices[:5]}...")

        self.setup_ui()

    def setup_ui(self):
        """Setup the test screen user interface"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Timer and question cards in upper left corner
        top_left_frame = tk.Frame(main_frame, bg='white')
        top_left_frame.pack(anchor='nw', pady=(0, 10))

        timer_frame = tk.Frame(top_left_frame, bg='white')
        timer_frame.pack(pady=(0, 10))

        timer_label = tk.Label(timer_frame, text="Time Remaining:", font=("Arial", 12, "bold"), bg='white')
        timer_label.pack()

        self.timer_display = tk.Label(timer_frame, text="03:00", font=("Arial", 20, "bold"),
                                    bg='white', fg='red')
        self.timer_display.pack()

        # Question cards under the timer
        cards_title = tk.Label(top_left_frame, text="Questions", font=("Arial", 12, "bold"), bg='white')
        cards_title.pack(pady=(10, 5))

        # Create 5x5 grid of question cards
        grid_frame = tk.Frame(top_left_frame, bg='white')
        grid_frame.pack()

        self.question_cards = []
        self.card_frames = []  # Store the border frames
        for row in range(5):  # Changed from 4 to 5
            for col in range(5):
                num = row * 5 + col + 1
                if num <= self.total_questions:
                    # Create a frame for the border (this will show the red/green color)
                    border_frame = tk.Frame(grid_frame, bg='red', bd=0)  # Start with red (unanswered)
                    border_frame.grid(row=row, column=col, padx=2, pady=2)

                    # Create the card inside the border frame
                    card = tk.Label(border_frame, text=str(num), font=("Arial", 10, "bold"),
                                  bg='white', width=4, height=2, relief=tk.FLAT)
                    card.pack(padx=3, pady=3)  # This creates the border effect
                    card.bind('<Button-1>', lambda e, q=num-1: self.jump_to_question(q))

                    self.question_cards.append(card)
                    self.card_frames.append(border_frame)

        # Title
        title = tk.Label(main_frame, text="Test Screen", font=("Arial", 24, "bold"), bg='white')
        title.pack(pady=10)

        # Center area for question display
        center_frame = tk.Frame(main_frame, bg='white')
        center_frame.pack(fill=tk.BOTH, expand=True)

        # Question display in center
        self.question_label = tk.Label(center_frame, text="", font=("Arial", 32, "bold"), bg='white')
        self.question_label.pack(expand=True)

        # Navigation area - bottom of main frame
        nav_frame = tk.Frame(main_frame, bg='white')
        nav_frame.pack(side=tk.BOTTOM, pady=20)

        # Input instruction
        instruction = tk.Label(nav_frame, text="Enter English translation:", font=("Arial", 14), bg='white')
        instruction.pack(pady=(0, 10))

        # Button and input layout using grid for reliable positioning
        button_input_frame = tk.Frame(nav_frame, bg='white')
        button_input_frame.pack()

        # Previous button (left)
        self.prev_button = tk.Button(button_input_frame, text="Previous", font=("Arial", 12),
                                   bg='lightgray', command=self.previous_question, width=10, height=2)
        self.prev_button.grid(row=0, column=0, padx=10, pady=5)

        # Input field (center)
        self.answer_entry = tk.Entry(button_input_frame, font=("Arial", 16), width=25, justify='center')
        self.answer_entry.grid(row=0, column=1, padx=10, pady=5)
        self.answer_entry.bind('<KeyRelease>', self.on_answer_changed)
        self.answer_entry.focus()

        # Next button (right)
        self.next_button = tk.Button(button_input_frame, text="Next", font=("Arial", 12),
                                   bg='lightgray', command=self.next_question, width=10, height=2)
        self.next_button.grid(row=0, column=2, padx=10, pady=5)

        # Finish Test button for easy testing (below the navigation buttons)
        finish_frame = tk.Frame(nav_frame, bg='white')
        finish_frame.pack(pady=(10, 0))

        self.finish_test_button = tk.Button(finish_frame, text="Finish Test (Testing)",
                                          font=("Arial", 12), bg='orange', fg='white',
                                          command=self.finish_test, width=20, height=2)
        self.finish_test_button.pack()

        # Start with first question
        self.display_current_question()

        # Start the 3-minute countdown timer
        self.start_timer()

    def start_timer(self):
        """Start the 3-minute countdown timer"""
        self.update_timer()

    def update_timer(self):
        """Update the countdown timer display"""
        if self.time_remaining > 0:
            minutes = self.time_remaining // 60
            seconds = self.time_remaining % 60
            time_text = f"{minutes:02d}:{seconds:02d}"

            if self.timer_display:
                self.timer_display.config(text=time_text)

                # Change color when time is running low
                if self.time_remaining <= 30:  # Last 30 seconds
                    self.timer_display.config(fg='red')
                elif self.time_remaining <= 60:  # Last minute
                    self.timer_display.config(fg='orange')
                else:
                    self.timer_display.config(fg='red')

            self.time_remaining -= 1

            # Schedule next update in 1 second
            self.root.after(1000, self.update_timer)
        else:
            # Time's up!
            if self.timer_display:
                self.timer_display.config(text="00:00", fg='red')
            self.on_timer_finished()

    def on_timer_finished(self):
        """Handle when the 3-minute timer reaches zero"""
        print("Test time finished!")
        # Save answers and complete the test
        self.save_answers_to_csv()
        if self.completion_callback:
            self.completion_callback(self.answers)
        else:
            # Show time's up message
            self.show_times_up_screen()

    def show_times_up_screen(self):
        """Show the time's up completion screen"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        completion_frame = tk.Frame(self.root, bg='white')
        completion_frame.pack(fill=tk.BOTH, expand=True)

        completion_label = tk.Label(
            completion_frame,
            text="Time's Up!\n\nTest Completed.\nThank you for your participation.",
            font=("Arial", 24, "bold"),
            bg='white',
            fg='black'
        )
        completion_label.pack(expand=True)

    def get_current_word_id(self):
        """Get the word_id for the current randomized question"""
        if self.current_question < len(self.question_indices):
            randomized_index = self.question_indices[self.current_question]
            if randomized_index < len(self.word_data):
                row = self.word_data.iloc[randomized_index]
                return row.get('word_id', randomized_index + 1)
        return None

    def display_current_question(self):
        """Display the current question (in randomized order)"""
        if self.current_question < len(self.question_indices):
            # Get the randomized question index
            randomized_index = self.question_indices[self.current_question]

            if randomized_index < len(self.word_data):
                row = self.word_data.iloc[randomized_index]
                icelandic_word = row.get('ice', '')
                word_id = row.get('word_id', randomized_index + 1)

                self.question_label.config(text=icelandic_word)

                # Show existing answer if any (stored by word_id)
                existing_answer = self.answers.get(word_id, '')
                self.answer_entry.delete(0, tk.END)
                self.answer_entry.insert(0, existing_answer)

                # Update card colors
                self.update_all_cards()

                # Update button states
                self.prev_button.config(state='normal' if self.current_question > 0 else 'disabled')
                self.next_button.config(state='normal' if self.current_question < self.total_questions - 1 else 'disabled')

    def update_all_cards(self):
        """Update all question card colors based on answer status"""
        for i in range(len(self.question_cards)):
            card = self.question_cards[i]
            border_frame = self.card_frames[i]

            # Get the word_id for this card position
            if i < len(self.question_indices):
                randomized_index = self.question_indices[i]
                if randomized_index < len(self.word_data):
                    row = self.word_data.iloc[randomized_index]
                    word_id = row.get('word_id', randomized_index + 1)

                    if word_id in self.answers and self.answers[word_id].strip():
                        # Answered - green border
                        border_frame.config(bg='green')
                    else:
                        # Unanswered - red border
                        border_frame.config(bg='red')

            # Current question highlight
            if i == self.current_question:
                card.config(bg='lightblue')
            else:
                card.config(bg='white')

    def on_answer_changed(self, event=None):
        """Handle answer change - save on every keystroke using word_id"""
        answer = self.answer_entry.get().strip()
        word_id = self.get_current_word_id()
        if word_id is not None:
            self.answers[word_id] = answer
            self.update_all_cards()

    def previous_question(self):
        """Go to previous question"""
        if self.current_question > 0:
            self.current_question -= 1
            self.display_current_question()

    def next_question(self):
        """Go to next question"""
        if self.current_question < self.total_questions - 1:
            self.current_question += 1
            self.display_current_question()

    def jump_to_question(self, question_index):
        """Jump to a specific question when card is clicked"""
        if 0 <= question_index < self.total_questions:
            self.current_question = question_index
            self.display_current_question()

    def save_answers_to_csv(self):
        """Save the answers to the CSV file in answ_1 column using word_id"""
        try:
            data_dir = "../data"
            if not os.path.exists(data_dir):
                print("Data directory not found")
                return

            csv_files = [f for f in os.listdir(data_dir)
                        if f.startswith(f"experiment_{self.unique_id}") and f.endswith('.csv')]

            if csv_files:
                csv_files.sort()
                latest_csv = os.path.join(data_dir, csv_files[-1])
                df = pd.read_csv(latest_csv)

                # Ensure word_id columns are the same type (int)
                df['word_id'] = df['word_id'].astype(int)

                print(f"Saving {len(self.answers)} answers to CSV...")

                # Update the answ_1 column with answers using word_id matching
                for word_id, answer in self.answers.items():
                    # Ensure word_id is int for matching
                    word_id = int(word_id)

                    # Find the row with matching word_id
                    matching_rows = df[df['word_id'] == word_id]
                    if not matching_rows.empty:
                        row_index = matching_rows.index[0]
                        df.loc[row_index, 'answ_1'] = answer
                        print(f"  Saved answer for word_id {word_id}: '{answer}'")
                    else:
                        print(f"  WARNING: No matching row found for word_id {word_id}")

                df.to_csv(latest_csv, index=False)
                print(f"✓ First test answers saved to {latest_csv}")
            else:
                print("No CSV file found to update")

        except Exception as e:
            print(f"Error saving answers: {e}")
            import traceback
            traceback.print_exc()

    def get_answers(self):
        """Get the current answers dictionary"""
        return self.answers.copy()

    def finish_test(self):
        """Finish the test immediately (for testing purposes)"""
        self.time_remaining = 0
        self.update_timer()
