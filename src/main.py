import tkinter as tk
from tkinter import ttk
import pandas as pd
import csv
import uuid
import os
import random
from datetime import datetime
from test_screen import TestScreen
from second_test_screen import SecondTestScreen

class ExperimentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cognitive Science Experiment")
        self.root.geometry("800x600")
        self.root.configure(bg='white')

        # Generate unique ID for this session
        self.unique_id = str(uuid.uuid4())[:8]  # Short unique ID

        # Load word data
        self.word_data = self.load_word_data()

        # Select random words for both phases
        self.select_random_word_sets()

        # Show welcome screen
        self.show_welcome_screen()

    def select_random_word_sets(self):
        """Select two sets of 25 random words for the two experiment phases"""
        total_words = len(self.word_data)

        if total_words < 50:
            print(f"Warning: Only {total_words} words available. Need at least 50 for two sets of 25.")
            # If we don't have enough words, use what we have
            all_indices = list(range(total_words))
            random.shuffle(all_indices)

            mid_point = min(25, total_words // 2)
            self.first_phase_indices = all_indices[:mid_point]
            self.second_phase_indices = all_indices[mid_point:min(mid_point * 2, total_words)]
        else:
            # Randomly select 50 unique indices
            all_indices = list(range(total_words))
            random.shuffle(all_indices)

            # First 25 for phase 1, next 25 for phase 2
            self.first_phase_indices = sorted(all_indices[:25])
            self.second_phase_indices = sorted(all_indices[25:50])

        # Create DataFrames for each phase - keep original indices for CSV matching
        # Reset index but keep the original word_id for matching
        self.first_phase_words = self.word_data.iloc[self.first_phase_indices].copy()
        self.first_phase_words.reset_index(drop=True, inplace=True)

        self.second_phase_words = self.word_data.iloc[self.second_phase_indices].copy()
        self.second_phase_words.reset_index(drop=True, inplace=True)

        print(f"Phase 1 word indices: {self.first_phase_indices}")
        print(f"Phase 2 word indices: {self.second_phase_indices}")
        print(f"Phase 1 first word: {self.first_phase_words.iloc[0]['ice']} -> {self.first_phase_words.iloc[0]['eng']} (word_id: {self.first_phase_words.iloc[0]['word_id']})")
        print(f"Phase 2 first word: {self.second_phase_words.iloc[0]['ice']} -> {self.second_phase_words.iloc[0]['eng']} (word_id: {self.second_phase_words.iloc[0]['word_id']})")

    def load_word_data(self):
        """Load word data from Excel file"""
        try:
            df = pd.read_excel('../word_pairs/Icelandic_English_Danish_words.xlsx')
            print(f"Excel file loaded successfully! Shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")

            # Check if the Excel file has the expected columns
            # Try different possible column name variations
            ice_col = None
            eng_col = None
            word_id_col = None

            # Look for Icelandic column (could be 'ice', 'icelandic', or index-based)
            for col in df.columns:
                col_str = str(col).lower()
                if 'ice' in col_str or 'island' in col_str:
                    ice_col = col
                    break

            # Look for English column (could be 'eng', 'english', or index-based)
            for col in df.columns:
                col_str = str(col).lower()
                if 'eng' in col_str or 'english' in col_str:
                    eng_col = col
                    break

            # Look for word_id column
            for col in df.columns:
                col_str = str(col).lower()
                if 'word_id' in col_str or 'id' in col_str:
                    word_id_col = col
                    break

            # If we can't find named columns, assume columns by position
            if ice_col is None and eng_col is None:
                if len(df.columns) >= 2:
                    # Assume first column is Icelandic, second is English
                    ice_col = df.columns[0]
                    eng_col = df.columns[1]

            print(f"Using columns - word_id: {word_id_col}, ice: {ice_col}, eng: {eng_col}")

            # Create standardized DataFrame
            result_data = []
            for index, row in df.iterrows():
                word_id = row[word_id_col] if word_id_col else index + 1
                ice_word = row[ice_col] if ice_col else ''
                eng_word = row[eng_col] if eng_col else ''

                result_data.append({
                    'word_id': word_id,
                    'ice': ice_word,
                    'eng': eng_word
                })

            result_df = pd.DataFrame(result_data)
            print(f"Processed {len(result_df)} word pairs")
            print("First few pairs:")
            for i in range(min(5, len(result_df))):
                row = result_df.iloc[i]
                print(f"  {i+1}: {row['ice']} -> {row['eng']}")

            return result_df

        except Exception as e:
            print(f"Error loading word data: {e}")
            # Create dummy data if file doesn't exist or can't be read
            return pd.DataFrame({
                'word_id': [1, 2, 3, 4, 5],
                'ice': ['hestur', 'hundur', 'köttur', 'fugl', 'fiskur'],
                'eng': ['horse', 'dog', 'cat', 'bird', 'fish']
            })

    def show_welcome_screen(self):
        """Display the welcome screen"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Welcome message
        welcome_label = tk.Label(
            main_frame,
            text="Welcome",
            font=("Arial", 32, "bold"),
            bg='white',
            fg='black'
        )
        welcome_label.pack(expand=True)

        # Next button in bottom right corner
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)

        next_button = tk.Button(
            button_frame,
            text="Next",
            font=("Arial", 14),
            bg='lightblue',
            command=self.on_next_clicked,
            width=10,
            height=2
        )
        next_button.pack(side=tk.RIGHT)

    def on_next_clicked(self):
        """Handle next button click - create CSV and show information screen"""
        self.create_csv_file()
        self.show_information_screen()

    def create_csv_file(self):
        """Create CSV file with unique name and populate with data"""
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../data/experiment_{self.unique_id}_{timestamp}.csv"

        # Ensure data directory exists
        os.makedirs("../data", exist_ok=True)

        # Prepare data for CSV
        csv_data = []

        # Add header
        csv_data.append(['id', 'word_id', 'ice', 'eng', 'answ_1', 'answ_2'])

        # Add data rows
        for index, row in self.word_data.iterrows():
            csv_row = [
                self.unique_id,  # unique id
                int(row.get('word_id', index + 1)),  # word_id from Excel or index
                row.get('ice', ''),  # Icelandic word
                row.get('eng', ''),  # English word
                '',  # answ_1 - empty for now
                ''   # answ_2 - empty for now
            ]
            csv_data.append(csv_row)

        # Write to CSV file
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(csv_data)
            print(f"CSV file created: {filename}")
        except Exception as e:
            print(f"Error creating CSV file: {e}")

    def show_information_screen(self):
        """Display the information screen with dummy text"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Information",
            font=("Arial", 24, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=(0, 20))

        # Create text frame with scrollbar
        text_frame = tk.Frame(main_frame, bg='white')
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Text widget with scrollbar
        text_widget = tk.Text(
            text_frame,
            font=("Arial", 12),
            bg='white',
            fg='black',
            wrap=tk.WORD,
            padx=10,
            pady=10
        )

        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        # Pack text widget and scrollbar
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Dummy text content
        dummy_text = """
                Welcome to this cognitive science experiment.
        
        We are very grateful for your participation.
        This experiment consists of several parts, including memorization and recall tasks.
        First you will be presented with a list of word pairs to memorize in 8 minutes.
        After a set period of time, you will be tested for 3 minutes on your memory of these word pairs.
        Then you will watch YouTube short for 8 minutes.
        Finally, you will be tested again on your memory of the word pairs for 3 minutes.
        Your responses will be recorded in a text file for analysis.
        
        If you have any questions, feel free to ask the experimenter before we begin.
        Remember you can leave the experiment at any time if you feel uncomfortable.
        Thank you again for your participation!
        """

        # Insert dummy text
        text_widget.insert(tk.END, dummy_text.strip())
        text_widget.config(state=tk.DISABLED)  # Make text read-only

        # Next button in bottom right corner
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))

        next_button = tk.Button(
            button_frame,
            text="Next",
            font=("Arial", 14),
            bg='lightblue',
            command=self.show_memorizing_screen,
            width=10,
            height=2
        )
        next_button.pack(side=tk.RIGHT)

    def show_memorizing_screen(self):
        """Display the memorizing screen with word pairs, information, and countdown timer"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main container
        main_container = tk.Frame(self.root, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Title (smaller)
        title_label = tk.Label(
            main_container,
            text="Memorizing Screen",
            font=("Arial", 16, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=(0, 5))

        # Create horizontal layout: word list on left, info panel on right
        content_frame = tk.Frame(main_container, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left side: Word pairs list (no scrollbar needed)
        list_frame = tk.Frame(content_frame, bg='white', relief=tk.RAISED, bd=1)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # List title (smaller)
        list_title = tk.Label(
            list_frame,
            text="Word Pairs",
            font=("Arial", 12, "bold"),
            bg='white',
            fg='black'
        )
        list_title.pack(pady=3)

        # Create container frame for word list (no canvas/scrollbar)
        words_container = tk.Frame(list_frame, bg='white')
        words_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Display word pairs as a compact list
        for index in range(len(self.first_phase_words)):
            row = self.first_phase_words.iloc[index]
            ice_word = row.get('ice', '')
            eng_word = row.get('eng', '')

            # Create frame for each word pair (minimal padding)
            pair_frame = tk.Frame(
                words_container,
                bg='white',
                relief=tk.FLAT,
                bd=0,
                padx=1,
                pady=0
            )
            pair_frame.pack(fill=tk.X, padx=1, pady=0)

            # Number label (smaller)
            number_label = tk.Label(
                pair_frame,
                text=f"{index + 1}.",
                font=("Arial", 9, "bold"),
                bg='white',
                fg='black',
                width=2,
                anchor='w'
            )
            number_label.pack(side=tk.LEFT, padx=(0, 2))

            # Icelandic word (no background color)
            ice_label = tk.Label(
                pair_frame,
                text=ice_word,
                font=("Arial", 10, "bold"),
                bg='white',
                fg='black',
                relief=tk.FLAT,
                padx=2,
                pady=0,
                width=18,
                anchor='w'
            )
            ice_label.pack(side=tk.LEFT, padx=1)

            # Arrow (smaller)
            arrow_label = tk.Label(
                pair_frame,
                text="→",
                font=("Arial", 10, "bold"),
                bg='white',
                fg='black'
            )
            arrow_label.pack(side=tk.LEFT, padx=1)

            # English word (no background color)
            eng_label = tk.Label(
                pair_frame,
                text=eng_word,
                font=("Arial", 10),
                bg='white',
                fg='black',
                relief=tk.FLAT,
                padx=2,
                pady=0,
                width=18,
                anchor='w'
            )
            eng_label.pack(side=tk.LEFT, padx=1)

        # Right side: Information panel and timer (more compact)
        info_panel = tk.Frame(content_frame, bg='lightgray', width=250, relief=tk.RAISED, bd=1)
        info_panel.pack(side=tk.RIGHT, fill=tk.Y)
        info_panel.pack_propagate(False)  # Maintain fixed width

        # Timer display
        timer_frame = tk.Frame(info_panel, bg='lightgray')
        timer_frame.pack(fill=tk.X, padx=5, pady=5)

        timer_label = tk.Label(
            timer_frame,
            text="Time Remaining:",
            font=("Arial", 10, "bold"),
            bg='lightgray',
            fg='black'
        )
        timer_label.pack()

        self.timer_display = tk.Label(
            timer_frame,
            text="08:00",
            font=("Arial", 20, "bold"),
            bg='lightgray',
            fg='red'
        )
        self.timer_display.pack()

        # Information text area
        info_title = tk.Label(
            info_panel,
            text="Instructions",
            font=("Arial", 11, "bold"),
            bg='lightgray',
            fg='black'
        )
        info_title.pack(pady=(5, 3))

        # Create scrollable text widget for information
        text_frame = tk.Frame(info_panel, bg='lightgray')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        info_text = tk.Text(
            text_frame,
            font=("Arial", 9),
            bg='white',
            fg='black',
            wrap=tk.WORD,
            height=8
        )

        info_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=info_text.yview)
        info_text.configure(yscrollcommand=info_scrollbar.set)

        info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Dummy instruction text
        instruction_text = """
        Study the word pairs carefully. You have 4 minutes to memorize the associations between the Icelandic and English words.

        After the time expires, you will be tested on your remembrance of these word pairs.

        Good luck with your memorization!
        """

        info_text.insert(tk.END, instruction_text.strip())
        info_text.config(state=tk.DISABLED)

        # Add a Next button for testing purposes
        next_button_frame = tk.Frame(info_panel, bg='lightgray')
        next_button_frame.pack(fill=tk.X, padx=5, pady=5)

        next_button = tk.Button(
            next_button_frame,
            text="Next (Testing)",
            font=("Arial", 10),
            bg='orange',
            fg='white',
            command=self.on_timer_finished,  # Use the same function as timer completion
            width=15,
            height=2
        )
        next_button.pack()

        # Start the countdown timer
        self.start_countdown_timer()

    def display_word_grid(self, parent_frame, word_data, start_index=0, count=25):
        """Display word pairs in a 5x5 grid"""
        # Get the word pairs from the specified range
        word_pairs = []
        end_index = min(start_index + count, len(word_data))

        for index in range(start_index, end_index):
            if index < len(word_data):
                row = word_data.iloc[index]
                ice_word = row.get('ice', '')
                eng_word = row.get('eng', '')
                if ice_word and eng_word:
                    word_pairs.append((ice_word, eng_word))

        # Pad to exactly 25 pairs if needed (5x5 grid)
        while len(word_pairs) < count:
            word_pairs.append(('', ''))

        # Create 5 rows x 5 columns grid
        for row in range(5):
            for col in range(5):
                index = row * 5 + col
                if index < len(word_pairs):
                    ice_word, eng_word = word_pairs[index]

                    # Create frame for word pair
                    pair_frame = tk.Frame(
                        parent_frame,
                        bg='white',
                        relief=tk.RAISED,
                        bd=1,
                        padx=5,
                        pady=5
                    )
                    pair_frame.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')

                    # Icelandic word (top)
                    ice_label = tk.Label(
                        pair_frame,
                        text=ice_word,
                        font=("Arial", 11, "bold"),
                        bg='lightblue',
                        fg='black',
                        relief=tk.FLAT,
                        padx=4,
                        pady=2
                    )
                    ice_label.pack(fill=tk.X)

                    # English word (bottom)
                    eng_label = tk.Label(
                        pair_frame,
                        text=eng_word,
                        font=("Arial", 11),
                        bg='lightgreen',
                        fg='black',
                        relief=tk.FLAT,
                        padx=4,
                        pady=2
                    )
                    eng_label.pack(fill=tk.X)

        # Configure grid weights for equal distribution
        for i in range(5):
            parent_frame.grid_rowconfigure(i, weight=1)
        for i in range(5):
            parent_frame.grid_columnconfigure(i, weight=1)

    def start_countdown_timer(self):
        """Start the 8-minute countdown timer for FIRST memorization"""
        self.time_remaining = 4 * 60  # 4 minutes in seconds
        self.update_first_timer()

    def update_first_timer(self):
        """Update the countdown timer display for FIRST memorization"""
        if hasattr(self, 'time_remaining') and self.time_remaining > 0:
            minutes = self.time_remaining // 60
            seconds = self.time_remaining % 60
            time_text = f"{minutes:02d}:{seconds:02d}"

            if hasattr(self, 'timer_display'):
                self.timer_display.config(text=time_text)

                # Change color when time is running low
                if self.time_remaining <= 60:  # Last minute
                    self.timer_display.config(fg='red')
                elif self.time_remaining <= 180:  # Last 3 minutes
                    self.timer_display.config(fg='orange')

            self.time_remaining -= 1

            # Schedule next update in 1 second
            self.root.after(1000, self.update_first_timer)
        else:
            # Time's up!
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text="00:00", fg='red')
            self.on_first_timer_finished()

    def on_first_timer_finished(self):
        """Handle when the FIRST countdown timer reaches zero"""
        print("First memorization time finished!")
        # Use the TestScreen module with first phase words
        self.test_screen = TestScreen(
            root=self.root,
            word_data=self.first_phase_words,
            unique_id=self.unique_id,
            completion_callback=self.on_first_test_completed
        )

    def on_first_test_completed(self, answers):
        """Handle FIRST test completion"""
        print(f"First test completed with {len(answers)} answers")
        # Show break screen
        self.show_break_screen()

    def start_second_countdown_timer(self):
        """Start the 4-minute countdown timer for SECOND memorization"""
        self.time_remaining_2 = 4 * 60  # 4 minutes in seconds
        self.update_second_timer()

    def update_second_timer(self):
        """Update the countdown timer display for SECOND memorization"""
        if hasattr(self, 'time_remaining_2') and self.time_remaining_2 > 0:
            minutes = self.time_remaining_2 // 60
            seconds = self.time_remaining_2 % 60
            time_text = f"{minutes:02d}:{seconds:02d}"

            if hasattr(self, 'timer_display'):
                self.timer_display.config(text=time_text)

                # Change color when time is running low
                if self.time_remaining_2 <= 60:  # Last minute
                    self.timer_display.config(fg='red')
                elif self.time_remaining_2 <= 180:  # Last 3 minutes
                    self.timer_display.config(fg='orange')

            self.time_remaining_2 -= 1

            # Schedule next update in 1 second
            self.root.after(1000, self.update_second_timer)
        else:
            # Time's up!
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text="00:00", fg='red')
            self.on_second_timer_finished()

    def on_second_timer_finished(self):
        """Handle when the SECOND countdown timer reaches zero"""
        print("Second memorization time finished!")
        # Use the SecondTestScreen module with second phase words
        self.second_test_screen = SecondTestScreen(
            root=self.root,
            word_data=self.second_phase_words,
            unique_id=self.unique_id,
            completion_callback=self.on_second_test_completed
        )

    def on_second_test_completed(self, answers):
        """Handle SECOND test completion"""
        print(f"Second test completed with {len(answers)} answers")
        # Show final completion screen
        self.show_final_completion_screen()

    def show_final_completion_screen(self):
        """Display the final results screen with calculated statistics"""
        # Calculate results from CSV
        results = self.calculate_results()

        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Experiment Complete - Results",
            font=("Arial", 28, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=(0, 20))

        # Results container with scrollbar
        results_frame = tk.Frame(main_frame, bg='white')
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Create canvas with scrollbar
        canvas = tk.Canvas(results_frame, bg='white')
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Display results
        if results:
            # Summary Section
            summary_frame = tk.Frame(scrollable_frame, bg='lightblue', relief=tk.RAISED, bd=2)
            summary_frame.pack(fill=tk.X, padx=10, pady=10)

            tk.Label(
                summary_frame,
                text="Summary Statistics",
                font=("Arial", 18, "bold"),
                bg='lightblue'
            ).pack(pady=10)

            # First Test Results
            first_test_frame = tk.Frame(summary_frame, bg='white', relief=tk.SOLID, bd=1)
            first_test_frame.pack(fill=tk.X, padx=20, pady=5)

            tk.Label(
                first_test_frame,
                text=f"First Test: {results['first_correct']}/{results['first_total']} correct ({results['first_percentage']:.1f}%)",
                font=("Arial", 14, "bold"),
                bg='white',
                fg='darkgreen' if results['first_percentage'] >= 50 else 'darkred'
            ).pack(pady=5)

            # Second Test Results
            second_test_frame = tk.Frame(summary_frame, bg='white', relief=tk.SOLID, bd=1)
            second_test_frame.pack(fill=tk.X, padx=20, pady=5)

            tk.Label(
                second_test_frame,
                text=f"Second Test: {results['second_correct']}/{results['second_total']} correct ({results['second_percentage']:.1f}%)",
                font=("Arial", 14, "bold"),
                bg='white',
                fg='darkgreen' if results['second_percentage'] >= 50 else 'darkred'
            ).pack(pady=5)

            # Overall Results
            overall_frame = tk.Frame(summary_frame, bg='white', relief=tk.SOLID, bd=1)
            overall_frame.pack(fill=tk.X, padx=20, pady=(5, 10))

            tk.Label(
                overall_frame,
                text=f"Overall: {results['total_correct']}/{results['total_answered']} correct ({results['overall_percentage']:.1f}%)",
                font=("Arial", 16, "bold"),
                bg='white',
                fg='blue'
            ).pack(pady=5)

            # Detailed Results Section
            details_frame = tk.Frame(scrollable_frame, bg='lightgray', relief=tk.RAISED, bd=2)
            details_frame.pack(fill=tk.X, padx=10, pady=10)

            tk.Label(
                details_frame,
                text="Detailed Results",
                font=("Arial", 16, "bold"),
                bg='lightgray'
            ).pack(pady=10)

            # First Test Details
            if results['first_details']:
                first_details_frame = tk.Frame(details_frame, bg='white', relief=tk.SOLID, bd=1)
                first_details_frame.pack(fill=tk.X, padx=10, pady=5)

                tk.Label(
                    first_details_frame,
                    text="First Test Answers:",
                    font=("Arial", 12, "bold"),
                    bg='white'
                ).pack(pady=5)

                for detail in results['first_details'][:10]:  # Show first 10
                    color = 'lightgreen' if detail['correct'] else 'lightcoral'
                    status = '✓' if detail['correct'] else '✗'

                    detail_label = tk.Label(
                        first_details_frame,
                        text=f"{status} {detail['ice']} → {detail['answer']} (correct: {detail['eng']})",
                        font=("Arial", 10),
                        bg=color,
                        anchor='w',
                        padx=10,
                        pady=2
                    )
                    detail_label.pack(fill=tk.X, padx=5, pady=1)

            # Second Test Details
            if results['second_details']:
                second_details_frame = tk.Frame(details_frame, bg='white', relief=tk.SOLID, bd=1)
                second_details_frame.pack(fill=tk.X, padx=10, pady=5)

                tk.Label(
                    second_details_frame,
                    text="Second Test Answers:",
                    font=("Arial", 12, "bold"),
                    bg='white'
                ).pack(pady=5)

                for detail in results['second_details'][:10]:  # Show first 10
                    color = 'lightgreen' if detail['correct'] else 'lightcoral'
                    status = '✓' if detail['correct'] else '✗'

                    detail_label = tk.Label(
                        second_details_frame,
                        text=f"{status} {detail['ice']} → {detail['answer']} (correct: {detail['eng']})",
                        font=("Arial", 10),
                        bg=color,
                        anchor='w',
                        padx=10,
                        pady=2
                    )
                    detail_label.pack(fill=tk.X, padx=5, pady=1)

            # Data saved message
            tk.Label(
                scrollable_frame,
                text=f"\nData saved to: {results['csv_file']}",
                font=("Arial", 10, "italic"),
                bg='white',
                fg='gray'
            ).pack(pady=10)

        else:
            # Error message if results couldn't be calculated
            tk.Label(
                scrollable_frame,
                text="Error calculating results.\nPlease check the data file.",
                font=("Arial", 16),
                bg='white',
                fg='red'
            ).pack(pady=50)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Thank you message at bottom
        thank_you_frame = tk.Frame(main_frame, bg='white')
        thank_you_frame.pack(side=tk.BOTTOM, pady=10)

        tk.Label(
            thank_you_frame,
            text="Thank you for your participation!",
            font=("Arial", 18, "bold"),
            bg='white',
            fg='green'
        ).pack()

    def calculate_results(self):
        """Calculate results from the CSV file"""
        try:
            data_dir = "../data"
            if not os.path.exists(data_dir):
                print("Data directory not found")
                return None

            # Find the CSV file for this session
            csv_files = [f for f in os.listdir(data_dir)
                        if f.startswith(f"experiment_{self.unique_id}") and f.endswith('.csv')]

            if not csv_files:
                print("No CSV file found")
                return None

            csv_files.sort()
            latest_csv = os.path.join(data_dir, csv_files[-1])

            print(f"Calculating results from: {latest_csv}")

            # Read the CSV file
            df = pd.read_csv(latest_csv)

            # Initialize counters
            first_correct = 0
            first_total = 0
            second_correct = 0
            second_total = 0

            first_details = []
            second_details = []

            # Process each row
            for _, row in df.iterrows():
                ice_word = str(row.get('ice', '')).strip().lower()
                eng_word = str(row.get('eng', '')).strip().lower()
                answer_1 = str(row.get('answ_1', '')).strip().lower()
                answer_2 = str(row.get('answ_2', '')).strip().lower()

                # Check first test answer
                if answer_1:
                    first_total += 1
                    is_correct = (answer_1 == eng_word)
                    if is_correct:
                        first_correct += 1
                    first_details.append({
                        'ice': row.get('ice', ''),
                        'eng': row.get('eng', ''),
                        'answer': row.get('answ_1', ''),
                        'correct': is_correct
                    })

                # Check second test answer
                if answer_2:
                    second_total += 1
                    is_correct = (answer_2 == eng_word)
                    if is_correct:
                        second_correct += 1
                    second_details.append({
                        'ice': row.get('ice', ''),
                        'eng': row.get('eng', ''),
                        'answer': row.get('answ_2', ''),
                        'correct': is_correct
                    })

            # Calculate percentages
            first_percentage = (first_correct / first_total * 100) if first_total > 0 else 0
            second_percentage = (second_correct / second_total * 100) if second_total > 0 else 0
            total_correct = first_correct + second_correct
            total_answered = first_total + second_total
            overall_percentage = (total_correct / total_answered * 100) if total_answered > 0 else 0

            results = {
                'first_correct': first_correct,
                'first_total': first_total,
                'first_percentage': first_percentage,
                'second_correct': second_correct,
                'second_total': second_total,
                'second_percentage': second_percentage,
                'total_correct': total_correct,
                'total_answered': total_answered,
                'overall_percentage': overall_percentage,
                'first_details': first_details,
                'second_details': second_details,
                'csv_file': latest_csv
            }

            print(f"Results calculated:")
            print(f"  First Test: {first_correct}/{first_total} ({first_percentage:.1f}%)")
            print(f"  Second Test: {second_correct}/{second_total} ({second_percentage:.1f}%)")
            print(f"  Overall: {total_correct}/{total_answered} ({overall_percentage:.1f}%)")

            return results

        except Exception as e:
            print(f"Error calculating results: {e}")
            import traceback
            traceback.print_exc()
            return None

    def on_timer_finished(self):
        """Handle when the first countdown timer reaches zero - compatibility method"""
        self.on_first_timer_finished()

    def show_break_screen(self):
        """Display the break screen with dummy text"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Break Time",
            font=("Arial", 32, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=(0, 30))

        # Create text frame with scrollbar
        text_frame = tk.Frame(main_frame, bg='white')
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Text widget with scrollbar
        text_widget = tk.Text(
            text_frame,
            font=("Arial", 14),
            bg='white',
            fg='black',
            wrap=tk.WORD,
            padx=20,
            pady=20
        )

        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        # Pack text widget and scrollbar
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Break screen dummy text
        break_text = """
        Great job completing the first test!

        You have now finished the first memory test.

        The next part of the experiment will begin when you click the "Next" button below.
        
        When you're ready to continue with the next phase of the experiment, please click the "Next" button.

        Thank you for your continued participation in this cognitive science research!
        """

        # Insert break text
        text_widget.insert(tk.END, break_text.strip())
        text_widget.config(state=tk.DISABLED)  # Make text read-only

        # Next button in bottom right corner
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))

        next_button = tk.Button(
            button_frame,
            text="Next",
            font=("Arial", 14),
            bg='lightgreen',
            command=self.on_break_next_clicked,
            width=10,
            height=2
        )
        next_button.pack(side=tk.RIGHT)

    def on_break_next_clicked(self):
        """Handle next button click from break screen"""
        print("Break completed, moving to second memorizing screen")
        # Show second memorizing screen before the second test
        self.show_second_memorizing_screen()

    def show_second_memorizing_screen(self):
        """Display the second memorizing screen with word pairs before the second test"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main container
        main_container = tk.Frame(self.root, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Title (smaller)
        title_label = tk.Label(
            main_container,
            text="Memorizing Screen - Round 2",
            font=("Arial", 16, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=(0, 5))

        # Create horizontal layout: word list on left, info panel on right
        content_frame = tk.Frame(main_container, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left side: Word pairs list (no scrollbar needed)
        list_frame = tk.Frame(content_frame, bg='white', relief=tk.RAISED, bd=1)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # List title (smaller)
        list_title = tk.Label(
            list_frame,
            text="Word Pairs",
            font=("Arial", 12, "bold"),
            bg='white',
            fg='black'
        )
        list_title.pack(pady=3)

        # Create container frame for word list (no canvas/scrollbar)
        words_container = tk.Frame(list_frame, bg='white')
        words_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Display word pairs as a compact list
        for index in range(len(self.second_phase_words)):
            row = self.second_phase_words.iloc[index]
            ice_word = row.get('ice', '')
            eng_word = row.get('eng', '')

            # Create frame for each word pair (minimal padding)
            pair_frame = tk.Frame(
                words_container,
                bg='white',
                relief=tk.FLAT,
                bd=0,
                padx=1,
                pady=0
            )
            pair_frame.pack(fill=tk.X, padx=1, pady=0)

            # Number label (smaller)
            number_label = tk.Label(
                pair_frame,
                text=f"{index + 1}.",
                font=("Arial", 9, "bold"),
                bg='white',
                fg='black',
                width=2,
                anchor='w'
            )
            number_label.pack(side=tk.LEFT, padx=(0, 2))

            # Icelandic word (no background color)
            ice_label = tk.Label(
                pair_frame,
                text=ice_word,
                font=("Arial", 10, "bold"),
                bg='white',
                fg='black',
                relief=tk.FLAT,
                padx=2,
                pady=0,
                width=18,
                anchor='w'
            )
            ice_label.pack(side=tk.LEFT, padx=1)

            # Arrow (smaller)
            arrow_label = tk.Label(
                pair_frame,
                text="→",
                font=("Arial", 10, "bold"),
                bg='white',
                fg='black'
            )
            arrow_label.pack(side=tk.LEFT, padx=1)

            # English word (no background color)
            eng_label = tk.Label(
                pair_frame,
                text=eng_word,
                font=("Arial", 10),
                bg='white',
                fg='black',
                relief=tk.FLAT,
                padx=2,
                pady=0,
                width=18,
                anchor='w'
            )
            eng_label.pack(side=tk.LEFT, padx=1)

        # Right side: Information panel and timer (more compact)
        info_panel = tk.Frame(content_frame, bg='lightgray', width=250, relief=tk.RAISED, bd=1)
        info_panel.pack(side=tk.RIGHT, fill=tk.Y)
        info_panel.pack_propagate(False)  # Maintain fixed width

        # Timer display
        timer_frame = tk.Frame(info_panel, bg='lightgray')
        timer_frame.pack(fill=tk.X, padx=5, pady=5)

        timer_label = tk.Label(
            timer_frame,
            text="Time Remaining:",
            font=("Arial", 10, "bold"),
            bg='lightgray',
            fg='black'
        )
        timer_label.pack()

        self.timer_display = tk.Label(
            timer_frame,
            text="08:00",
            font=("Arial", 20, "bold"),
            bg='lightgray',
            fg='red'
        )
        self.timer_display.pack()

        # Information text area
        info_title = tk.Label(
            info_panel,
            text="Instructions",
            font=("Arial", 11, "bold"),
            bg='lightgray',
            fg='black'
        )
        info_title.pack(pady=(5, 3))

        # Create scrollable text widget for information
        text_frame = tk.Frame(info_panel, bg='lightgray')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        info_text = tk.Text(
            text_frame,
            font=("Arial", 9),
            bg='white',
            fg='black',
            wrap=tk.WORD,
            height=8
        )

        info_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=info_text.yview)
        info_text.configure(yscrollcommand=info_scrollbar.set)

        info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add instruction text for second memorization session
        instruction_text = """
        Review the word pairs again. You have 4 minutes to refresh your memory of the associations between the Icelandic and English words.

        After the time expires, you will be tested again on your remembrance of these word pairs. The questions will be presented in a different order.

        Good luck with your second memorization session!
        """

        info_text.insert(tk.END, instruction_text.strip())
        info_text.config(state=tk.DISABLED)

        # Add a Next button for testing purposes
        next_button_frame = tk.Frame(info_panel, bg='lightgray')
        next_button_frame.pack(fill=tk.X, padx=5, pady=5)

        next_button = tk.Button(
            next_button_frame,
            text="Next (Testing)",
            font=("Arial", 10),
            bg='orange',
            fg='white',
            command=self.on_second_timer_finished,
            width=15,
            height=2
        )
        next_button.pack()

        # Start the countdown timer for second memorization
        self.start_second_countdown_timer()

def main():
    root = tk.Tk()
    app = ExperimentApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
