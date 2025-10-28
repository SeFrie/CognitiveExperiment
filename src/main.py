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
import textwrap

class ExperimentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cognitive Science Experiment")
        self.root.geometry("1200x800")
        self.root.configure(bg='white')

        # Generate unique ID for this session
        self.unique_id = str(uuid.uuid4())[:8]  # Short unique ID

        # Initialize personalization flag (will be set based on button click)
        self.personalization_flag = None

        # Initialize Icelandic knowledge flag (will be set based on rating)
        self.knows_icelandic = None

        # Initialize YouTube usage rating (will be set based on button click)
        self.youtube_usage = None

        # Load word data
        self.word_data = self.load_word_data()

        # Select random words for both phases
        self.select_random_word_sets()

        # Show welcome screen
        self.show_welcome_screen()

    def create_footer(self, parent_frame):
        """Create a standard footer for all screens"""
        footer_frame = tk.Frame(parent_frame, bg='#990000', height=40)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)
        footer_frame.pack_propagate(False)  # Maintain fixed height
        
        # Footer content text
        footer_label = tk.Label(
            footer_frame,
            text="This experiment is conducted as part of a research study | Session ID: " + self.unique_id,
            font=("Arial", 10),
            bg='#990000',
            fg='white'
        )
        footer_label.pack(pady=10)
        
        return footer_frame
        
        return footer_frame

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
            df = pd.read_excel('word_pairs/Icelandic-English-Danish_40Words.xlsx')
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

        # Create footer
        self.create_footer(main_frame)

        # Next button in upper right corner
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=20)

        # Welcome message
        welcome_label = tk.Label(
            main_frame,
            text="Welcome",
            font=("Arial", 52, "bold"),
            bg='white',
            fg='black'
        )
        welcome_label.pack(expand=True)

        # Icelandic knowledge question frame
        icelandic_frame = tk.Frame(main_frame, bg='white')
        icelandic_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(10, 10))

        # Question label
        question_label = tk.Label(
            icelandic_frame,
            text="Do you know Icelandic?",
            font=("Arial", 20, "bold"),
            bg='white',
            fg='black'
        )
        question_label.pack(pady=(0, 10))

        # Radio buttons frame for Yes/No
        icelandic_buttons_frame = tk.Frame(icelandic_frame, bg='white')
        icelandic_buttons_frame.pack()

        # Variable to store Icelandic knowledge choice
        self.icelandic_var = tk.StringVar(value="")

        # Yes radio button
        yes_radio = tk.Radiobutton(
            icelandic_buttons_frame,
            text="Yes",
            variable=self.icelandic_var,
            value="Yes",
            font=("Arial", 16),
            bg='white',
            activebackground='lightgreen',
            selectcolor='lightgreen',
            command=self.on_icelandic_changed,
            indicatoron=True
        )
        yes_radio.pack(side=tk.LEFT, padx=20)

        # No radio button
        no_radio = tk.Radiobutton(
            icelandic_buttons_frame,
            text="No",
            variable=self.icelandic_var,
            value="No",
            font=("Arial", 16),
            bg='white',
            activebackground='lightcoral',
            selectcolor='lightcoral',
            command=self.on_icelandic_changed,
            indicatoron=True
        )
        no_radio.pack(side=tk.LEFT, padx=20)

        # Personalization buttons frame
        personalization_frame = tk.Frame(main_frame, bg='white')
        personalization_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(10, 20))

        # Personalized button (initially disabled)
        self.personalized_button = tk.Button(
            personalization_frame,
            text="Personalized",
            font=("Arial", 14),
            bg='lightgray',
            command=self.on_personalized_clicked,
            width=20,
            height=2,
            state=tk.DISABLED
        )
        self.personalized_button.pack(side=tk.LEFT, padx=5)

        # Non-personalized button (initially disabled)
        self.non_personalized_button = tk.Button(
            personalization_frame,
            text="Non-Personalized",
            font=("Arial", 14),
            bg='lightgray',
            command=self.on_non_personalized_clicked,
            width=20,
            height=2,
            state=tk.DISABLED
        )
        self.non_personalized_button.pack(side=tk.RIGHT, padx=5)

        # YouTube usage rating frame
        youtube_frame = tk.Frame(main_frame, bg='white')
        youtube_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(10, 10))

        # Question label
        youtube_label = tk.Label(
            youtube_frame,
            text="How much time do you spend on YouTube Shorts per day?",
            font=("Arial", 20, "bold"),
            bg='white',
            fg='black'
        )
        youtube_label.pack(pady=(0, 10))

        # Radio buttons frame for time options
        youtube_buttons_frame = tk.Frame(youtube_frame, bg='white')
        youtube_buttons_frame.pack()

        # Variable to store YouTube usage choice
        self.youtube_var = tk.StringVar(value="")

        # 0-15 min radio button
        min_15_radio = tk.Radiobutton(
            youtube_buttons_frame,
            text="0-15 minutes",
            variable=self.youtube_var,
            value="0-15 minutes",
            font=("Arial", 16),
            bg='white',
            activebackground='lightgreen',
            selectcolor='lightgreen',
            command=self.on_youtube_changed,
            indicatoron=True
        )
        min_15_radio.pack(side=tk.LEFT, padx=15)

        # 16-45 min radio button
        min_45_radio = tk.Radiobutton(
            youtube_buttons_frame,
            text="16-45 minutes",
            variable=self.youtube_var,
            value="16-45 minutes",
            font=("Arial", 16),
            bg='white',
            activebackground='lightyellow',
            selectcolor='lightyellow',
            command=self.on_youtube_changed,
            indicatoron=True
        )
        min_45_radio.pack(side=tk.LEFT, padx=15)

        # More than 45 min radio button
        more_45_radio = tk.Radiobutton(
            youtube_buttons_frame,
            text="More than 45 minutes",
            variable=self.youtube_var,
            value="More than 45 minutes",
            font=("Arial", 16),
            bg='white',
            activebackground='lightcoral',
            selectcolor='lightcoral',
            command=self.on_youtube_changed,
            indicatoron=True
        )
        more_45_radio.pack(side=tk.LEFT, padx=15)

    def check_and_enable_buttons(self):
        """Check if both radio button groups have selections and enable personalization buttons"""
        if self.icelandic_var.get() and self.youtube_var.get():
            # Both selections made - enable the buttons with proper colors
            self.personalized_button.config(state=tk.NORMAL, bg='lightgreen')
            self.non_personalized_button.config(state=tk.NORMAL, bg='lightcoral')
        else:
            # Not both selected - keep buttons disabled
            self.personalized_button.config(state=tk.DISABLED, bg='lightgray')
            self.non_personalized_button.config(state=tk.DISABLED, bg='lightgray')

    def on_icelandic_changed(self):
        """Handle Icelandic knowledge radio button change"""
        self.knows_icelandic = self.icelandic_var.get()
        print(f"Icelandic knowledge: {self.knows_icelandic}")
        # Check if we should enable the personalization buttons
        self.check_and_enable_buttons()

    def on_youtube_changed(self):
        """Handle YouTube usage radio button change"""
        self.youtube_usage = self.youtube_var.get()
        print(f"YouTube usage: {self.youtube_usage}")
        # Check if we should enable the personalization buttons
        self.check_and_enable_buttons()


    def on_icelandic_yes_clicked(self):
        """Handle Icelandic Yes button click"""
        print("Icelandic knowledge: Yes")
        self.knows_icelandic = "Yes"

    def on_icelandic_no_clicked(self):
        """Handle Icelandic No button click"""
        print("Icelandic knowledge: No")
        self.knows_icelandic = "No"

    def on_personalized_clicked(self):
        """Handle personalized button click"""
        print("Personalized option selected")
        self.personalization_flag = True  # Set flag for personalized
        self.create_csv_file()  # Create CSV file
        self.show_information_screen()  # Show information screen

    def on_non_personalized_clicked(self):
        """Handle non-personalized button click"""
        print("Non-personalized option selected")
        self.personalization_flag = False  # Set flag for non-personalized
        self.create_csv_file()  # Create CSV file
        self.show_information_screen()  # Show information screen

    def on_youtube_usage_selected(self, option):
        """Handle YouTube usage rating button click"""
        if option == 1:
            print("YouTube usage: 0-15 minutes")
            self.youtube_usage = "0-15 minutes"
        elif option == 2:
            print("YouTube usage: 16-45 minutes")
            self.youtube_usage = "16-45 minutes"
        elif option == 3:
            print("YouTube usage: More than 45 minutes")
            self.youtube_usage = "More than 45 minutes"

        # Optionally, you can directly show the information screen after selection
        # self.show_information_screen()

    def on_next_clicked(self):
        """Handle next button click - create CSV and show information screen"""
        self.create_csv_file()
        self.show_information_screen()

    def create_csv_file(self):
        """Create CSV file with unique name and populate with data"""
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/experiment_{self.unique_id}_{timestamp}.csv"

        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        # Prepare data for CSV
        csv_data = []

        # Add header with condition, knows_icelandic, and youtube_usage columns
        csv_data.append(['id', 'word_id', 'ice', 'eng', 'answer', 'test_id', 'condition', 'knows_icelandic', 'youtube_usage'])

        # Determine conditions based on personalization choice
        # Personalized: First test gets P, Second test gets N
        # Non-personalized: First test gets N, Second test gets P
        first_test_condition = 'P' if self.personalization_flag else 'N'
        second_test_condition = 'N' if self.personalization_flag else 'P'

        # Add data rows for FIRST TEST (test_id = 0)
        for index, row in self.first_phase_words.iterrows():
            csv_row = [
                self.unique_id,  # unique id
                int(row.get('word_id', index + 1)),  # word_id from Excel
                row.get('ice', ''),  # Icelandic word
                row.get('eng', ''),  # English word
                '',  # answer - empty for now, will be filled by test screen
                0,  # test_id - 0 for first test
                first_test_condition,  # condition for first test
                self.knows_icelandic if self.knows_icelandic else '',  # knows_icelandic
                self.youtube_usage if self.youtube_usage else ''  # youtube_usage
            ]
            csv_data.append(csv_row)

        # Add data rows for SECOND TEST (test_id = 1)
        for index, row in self.second_phase_words.iterrows():
            csv_row = [
                self.unique_id,  # unique id
                int(row.get('word_id', index + 1)),  # word_id from Excel
                row.get('ice', ''),  # Icelandic word
                row.get('eng', ''),  # English word
                '',  # answer - empty for now, will be filled by test screen
                1,  # test_id - 1 for second test
                second_test_condition,  # condition for second test
                self.knows_icelandic if self.knows_icelandic else '',  # knows_icelandic
                self.youtube_usage if self.youtube_usage else ''  # youtube_usage
            ]
            csv_data.append(csv_row)

        # Store the initial choice for test screens to use
        self.csv_filename = filename

        # Write to CSV file
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(csv_data)
            print(f"CSV file created: {filename}")
            print(f"Initial personalization choice: {'Personalized' if self.personalization_flag else 'Non-personalized'}")
            print(f"Knows Icelandic: {self.knows_icelandic if self.knows_icelandic else 'Not specified'}")
            print(f"YouTube usage: {self.youtube_usage if self.youtube_usage else 'Not specified'}")
            print(f"Test 1 will use condition: {first_test_condition}")
            print(f"Test 2 will use condition: {second_test_condition}")
            print(f"Total rows created: {len(csv_data) - 1} (25 for Test 1, 25 for Test 2)")
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

        # Create footer
        self.create_footer(main_frame)

        # Top bar with title and Next button
        top_bar = tk.Frame(main_frame, bg='white')
        top_bar.pack(fill=tk.X, pady=(0, 20))

        # Title on the left
        title_label = tk.Label(
            top_bar,
            text="Information",
            font=("Arial", 24, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(side=tk.LEFT)

        # Next button on the right
        next_button = tk.Button(
            top_bar,
            text="Next",
            font=("Arial", 14),
            bg='lightblue',
            command=self.show_memorizing_screen,
            width=10,
            height=2
        )
        next_button.pack(side=tk.RIGHT)

        # Create text frame with scrollbar
        text_frame = tk.Frame(main_frame, bg='white')
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Text widget with scrollbar
        text_widget = tk.Text(
            text_frame,
            font=("Arial", 18),
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
        
        text_widget.tag_configure("left", justify='left')


        # Dummy text content
        information_text = textwrap.dedent("""
        Welcome to this cognitive science experiment.
        
        We are very grateful for your participation.
        This experiment consists of several parts, including memorization and recall tasks.
        First you will be presented with a list of 20 word pairs to memorize in 4 minutes.
        Then you will watch YouTube short videos for 8 minutes, the examiner will tell you on which account.
        
        Afterwards, you will be tested for 3 minutes on your memory of these word pairs.
        You will then be presented with another list of 20 word pairs to memorize in 4 minutes.
        Then watch YouTube short videos for another 8 minutes.
        Finally, you will be tested again on your memory of the 20 new word pairs for 3 minutes.
        Your responses will be recorded in a csv file for analysis.
        
        If you have any questions, feel free to ask the experimenter before we begin.
        Remember you can leave the experiment at any time if you feel uncomfortable.
        Thank you again for your participation!
        """)

        # Insert information text
        text_widget.insert(tk.END, information_text.strip(), "left")
        text_widget.config(state=tk.DISABLED)  # Make text read-only

    def show_memorizing_screen(self):
        """Display the memorizing screen with word pairs, information, and countdown timer"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main container
        main_container = tk.Frame(self.root, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create footer
        self.create_footer(main_container)

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
            font=("Arial", 16, "bold"),
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
                padx=0,
                pady=0
            )
            pair_frame.pack(padx=0, pady=0)

            # Number label (smaller)
            number_label = tk.Label(
                pair_frame,
                text=f"{index + 1}.",
                font=("Arial", 12, "bold"),
                bg='white',
                fg='black',
                width=2,
                anchor='e'
            )
            number_label.pack(side=tk.LEFT, padx=(0, 3))

            # Icelandic word (centered, right-aligned)
            ice_label = tk.Label(
                pair_frame,
                text=ice_word,
                font=("Arial", 16, "bold"),
                bg='white',
                fg='black',
                relief=tk.FLAT,
                padx=3,
                pady=0,
                width=18,
                anchor='e'
            )
            ice_label.pack(side=tk.LEFT, padx=1)

            # Arrow (bigger and centered)
            arrow_label = tk.Label(
                pair_frame,
                text="→",
                font=("Arial", 16, "bold"),
                bg='white',
                fg='darkblue',
                width=2
            )
            arrow_label.pack(side=tk.LEFT, padx=5)

            # English word (centered, left-aligned)
            eng_label = tk.Label(
                pair_frame,
                text=eng_word,
                font=("Arial", 16, "bold"),
                bg='white',
                fg='black',
                relief=tk.FLAT,
                padx=3,
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
            fg='red'  # Red color
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

        After the time has elapsed, you will be tested on your memory of these word pairs.

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
            fg='black',
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
                # Keep red color throughout
                self.timer_display.config(fg='red')

            self.time_remaining -= 1

            # Schedule next update in 1 second and store the timer ID
            self.first_timer_id = self.root.after(1000, self.update_first_timer)
        else:
            # Time's up!
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text="00:00", fg='red')
            self.on_first_timer_finished()

    def on_first_timer_finished(self):
        """Handle when the FIRST countdown timer reaches zero"""
        print("First memorization time finished!")
        # Show first break screen after first memorization
        self.show_first_break_screen()

    def on_first_test_completed(self, answers):
        """Handle FIRST test completion"""
        print(f"First test completed with {len(answers)} answers")
        # After first test, show 20-second break before second memorizing screen
        self.show_intermediate_break_screen()

    def show_intermediate_break_screen(self):
        """Display a 10-second break screen between first test and second memorizing screen"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create footer
        self.create_footer(main_frame)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Break Time - 10 Seconds",
            font=("Arial", 32, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=(50, 20))

        # Countdown timer display
        self.timer_display = tk.Label(
            main_frame,
            text="20",
            font=("Arial", 72, "bold"),
            bg='white',
            fg='red'
        )
        self.timer_display.pack(pady=40)

        # Instructions
        instruction_text = tk.Label(
            main_frame,
            text="Please get ready for the next test.\n"
            "The second memorization session will begin shortly.",
            
            font=("Arial", 18),
            bg='white',
            fg='black',
            justify=tk.CENTER
        )
        instruction_text.pack(pady=20)

        # Skip button for testing
        skip_button = tk.Button(
            main_frame,
            text="Skip Break",
            font=("Arial", 16),
            bg='orange',
            fg='black',
            command=self.skip_intermediate_break,
            width=20,
            height=2
        )
        skip_button.pack(pady=10)

        # Start the 10-second countdown
        self.intermediate_break_countdown = 10
        self.start_intermediate_break_countdown()

    def start_intermediate_break_countdown(self):
        """Start the countdown timer for the intermediate break"""
        if self.intermediate_break_countdown > 0:
            self.timer_display.config(text=str(self.intermediate_break_countdown))
            self.intermediate_break_countdown -= 1
            self.intermediate_break_timer_id = self.root.after(1000, self.start_intermediate_break_countdown)
        else:
            # Timer finished, proceed to second memorizing screen
            self.show_second_memorizing_screen()

    def skip_intermediate_break(self):
        """Skip the intermediate break countdown"""
        # Cancel the timer if it's running
        if hasattr(self, 'intermediate_break_timer_id'):
            try:
                self.root.after_cancel(self.intermediate_break_timer_id)
            except:
                pass
        # Proceed directly to second memorizing screen
        self.show_second_memorizing_screen()

    def show_first_break_screen(self):
        """Display the first 8-minute break screen after second memorization"""
        # Cancel the first memorization timer to prevent interference
        if hasattr(self, 'first_timer_id'):
            try:
                self.root.after_cancel(self.first_timer_id)
            except:
                pass

        if hasattr(self, 'time_remaining'):
            self.time_remaining = 0 # Stop the timer from continuing

        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create footer
        self.create_footer(main_frame)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Break Time - 8 Minutes",
            font=("Arial", 32, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=(0, 20))

        # Countdown timer display
        self.timer_display = tk.Label(
            main_frame,
            text="08:00",
            font=("Arial", 48, "bold"),
            bg='white',
            fg='red'  # Red color
        )
        self.timer_display.pack(pady=20)

        # Instructions
        instruction_text = tk.Label(
            main_frame,
            text="Please open Youtube Shorts on your phone like the examiner told you."
                 "\nPlease spend the next 8 minutes scrolling through YouTube Short videos."
                 "\nThe memorization session will begin when the timer expires.",


            font=("Arial", 14),
            bg='white',
            fg='black',
            justify=tk.CENTER
        )
        instruction_text.pack(pady=20)

        # Skip button for testing
        next_button = tk.Button(
            main_frame,
            text="Skip Break (Testing)",
            font=("Arial", 12),
            bg='orange',
            fg='black',
            command=self.on_first_break_finished,
            width=20,
            height=2
        )
        next_button.pack(pady=10)

        # Start the 8-minute break timer
        self.break_time_remaining = 8 * 60
        self.update_first_break_timer()

    def update_first_break_timer(self):
        """Update the first break timer display"""
        if hasattr(self, 'break_time_remaining') and self.break_time_remaining > 0:
            minutes = self.break_time_remaining // 60
            seconds = self.break_time_remaining % 60
            time_text = f"{minutes:02d}:{seconds:02d}"

            # Color changes based on time remaining
            if self.break_time_remaining <= 60:
                color = 'red'
            elif self.break_time_remaining <= 180:
                color = 'orange'
            else:
                color = 'blue'

            if hasattr(self, 'timer_display'):
                self.timer_display.config(text=time_text, fg=color)

            self.break_time_remaining -= 1
            self.break_timer_id = self.root.after(1000, self.update_first_break_timer)
        else:
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text="00:00", fg='red')
            self.on_first_break_finished()

    def on_first_break_finished(self):
        """Handle when first break finishes"""
        # Cancel the break timer to prevent interference
        if hasattr(self, 'break_timer_id'):
            try:
                self.root.after_cancel(self.break_timer_id)
            except:
                pass

        print("First break finished! Showing get ready screen...")
        # After first break, show get ready screen before first test
        self.show_first_get_ready_screen()

    def show_first_get_ready_screen(self):
        """Display the get ready screen before first test with 20 second countdown"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create footer
        self.create_footer(main_frame)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Get ready for the next test",
            font=("Arial", 36, "bold"),
            bg='white',
            fg='darkblue'
        )
        title_label.pack(pady=(50, 30))

        # Countdown timer display
        self.timer_display = tk.Label(
            main_frame,
            text="20",
            font=("Arial", 72, "bold"),
            bg='white',
            fg='red'
        )
        self.timer_display.pack(pady=40)

        # Instructions
        instruction_text = tk.Label(
            main_frame,
            text="The test will start in 10 seconds.\n\nPlease get ready!",
            font=("Arial", 18),
            bg='white',
            fg='black',
            justify=tk.CENTER
        )
        instruction_text.pack(pady=30)

        # Skip button
        skip_button = tk.Button(
            main_frame,
            text="Skip Break",
            command=self.skip_first_get_ready,
            font=("Arial", 16),
            bg='lightblue',
            fg='black',
            width=15,
            height=2,
            relief=tk.RAISED,
            bd=3
        )
        skip_button.pack(pady=20)

        # Start the 10-second countdown timer
        self.get_ready_time_remaining = 10
        self.update_first_get_ready_timer()

    def update_first_get_ready_timer(self):
        """Update the get ready timer display for first test"""
        if hasattr(self, 'get_ready_time_remaining') and self.get_ready_time_remaining > 0:
            time_text = str(self.get_ready_time_remaining)

            if hasattr(self, 'timer_display'):
                self.timer_display.config(text=time_text)
                # Change color based on time remaining
                if self.get_ready_time_remaining <= 5:
                    self.timer_display.config(fg='red')
                elif self.get_ready_time_remaining <= 10:
                    self.timer_display.config(fg='orange')
                else:
                    self.timer_display.config(fg='darkblue')

            self.get_ready_time_remaining -= 1
            self.get_ready_timer_id = self.root.after(1000, self.update_first_get_ready_timer)
        else:
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text="0", fg='red')
            self.on_first_get_ready_finished()

    def on_first_get_ready_finished(self):
        """Handle when first get ready timer finishes"""
        # Cancel the timer to prevent interference
        if hasattr(self, 'get_ready_timer_id'):
            try:
                self.root.after_cancel(self.get_ready_timer_id)
            except:
                pass

        print("Get ready finished! Starting first test...")
        # Start first test screen
        self.test_screen = TestScreen(
            root=self.root,
            word_data=self.first_phase_words,
            unique_id=self.unique_id,
            personalization_flag=self.personalization_flag,
            completion_callback=self.on_first_test_completed
        )

    def skip_first_get_ready(self):
        """Skip the first get ready countdown and start test immediately"""
        # Cancel the timer
        if hasattr(self, 'get_ready_timer_id'):
            try:
                self.root.after_cancel(self.get_ready_timer_id)
            except:
                pass
        
        # Reset the time remaining to trigger the finished callback
        self.get_ready_time_remaining = 0
        self.on_first_get_ready_finished()

    def start_second_countdown_timer(self):
        """Start the 4-minute countdown timer for SECOND memorization"""
        # Cancel any existing timer callbacks to prevent conflicts
        if hasattr(self, 'second_timer_id'):
            try:
                self.root.after_cancel(self.second_timer_id)
            except:
                pass

        # Reset the timer to 4 minutes
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
                # Keep red color throughout
                self.timer_display.config(fg='red')

            self.time_remaining_2 -= 1

            # Schedule next update in 1 second and store the timer ID
            self.second_timer_id = self.root.after(1000, self.update_second_timer)
        else:
            # Time's up!
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text="00:00", fg='red')
            self.on_second_timer_finished()

    def on_second_timer_finished(self):
        """Handle when the SECOND countdown timer reaches zero"""
        print("Second memorization time finished!")
        # Show second break screen after second memorization
        self.show_second_break_screen()

    def show_second_break_screen(self):
        """Display the second 8-minute break screen after second memorization"""
        # Cancel the second memorization timer to prevent interference
        if hasattr(self, 'second_timer_id'):
            try:
                self.root.after_cancel(self.second_timer_id)
            except:
                pass

        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create footer
        self.create_footer(main_frame)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Break Time - 8 Minutes",
            font=("Arial", 32, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=(0, 20))

        # Countdown timer display
        self.timer_display = tk.Label(
            main_frame,
            text="08:00",
            font=("Arial", 48, "bold"),
            bg='white',
            fg='red'
        )
        self.timer_display.pack(pady=20)

        # Instructions
        instruction_text = tk.Label(
            main_frame,
            text="Please open Youtube Shorts on your phone like the examiner told you."
                 "\nPlease spend the next 8 minutes scrolling through YouTube Short videos."
                 "\nThe memorization session will begin when the timer expires.", 
            font=("Arial", 14),
            bg='white',
            fg='black',
            justify=tk.CENTER
        )
        instruction_text.pack(pady=20)

        # Skip button for testing
        next_button = tk.Button(
            main_frame,
            text="Skip Break (Testing)",
            font=("Arial", 12),
            bg='orange',
            fg='black',
            command=self.on_second_break_finished,
            width=20,
            height=2
        )
        next_button.pack(pady=10)

        # Start the 8-minute break timer
        self.second_break_time_remaining = 8 * 60
        self.update_second_break_timer()

    def update_second_break_timer(self):
        """Update the second break timer display"""
        if hasattr(self, 'second_break_time_remaining') and self.second_break_time_remaining > 0:
            minutes = self.second_break_time_remaining // 60
            seconds = self.second_break_time_remaining % 60
            time_text = f"{minutes:02d}:{seconds:02d}"

            # Color changes based on time remaining
            if self.second_break_time_remaining <= 60:
                color = 'red'
            elif self.second_break_time_remaining <= 180:
                color = 'orange'
            else:
                color = 'blue'

            if hasattr(self, 'timer_display'):
                self.timer_display.config(text=time_text, fg=color)

            self.second_break_time_remaining -= 1
            self.second_break_timer_id = self.root.after(1000, self.update_second_break_timer)
        else:
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text="00:00", fg='red')
            self.on_second_break_finished()

    def on_second_break_finished(self):
        """Handle when second break finishes"""
        # Cancel the break timer to prevent interference
        if hasattr(self, 'second_break_timer_id'):
            try:
                self.root.after_cancel(self.second_break_timer_id)
            except:
                pass

        print("Second break finished! Showing get ready screen...")
        # After second break, show get ready screen before second test
        self.show_second_get_ready_screen()

    def show_second_get_ready_screen(self):
        """Display the get ready screen before second test with 20 second countdown"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Create footer
        self.create_footer(main_frame)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Get ready for the next test",
            font=("Arial", 36, "bold"),
            bg='white',
            fg='darkblue'
        )
        title_label.pack(pady=(50, 30))

        # Countdown timer display
        self.timer_display = tk.Label(
            main_frame,
            text="20",
            font=("Arial", 72, "bold"),
            bg='white',
            fg='red'
        )
        self.timer_display.pack(pady=40)

        # Instructions
        instruction_text = tk.Label(
            main_frame,
            text="The test will start in 10 seconds.\n\nPlease get ready!",
            font=("Arial", 18),
            bg='white',
            fg='black',
            justify=tk.CENTER
        )
        instruction_text.pack(pady=30)

        # Skip button
        skip_button = tk.Button(
            main_frame,
            text="Skip Break",
            command=self.skip_second_get_ready,
            font=("Arial", 16),
            bg='lightblue',
            fg='black',
            width=15,
            height=2,
            relief=tk.RAISED,
            bd=3
        )
        skip_button.pack(pady=20)

        # Start the 10-second countdown timer
        self.get_ready_time_remaining_2 = 10
        self.update_second_get_ready_timer()

    def update_second_get_ready_timer(self):
        """Update the get ready timer display for second test"""
        if hasattr(self, 'get_ready_time_remaining_2') and self.get_ready_time_remaining_2 > 0:
            time_text = str(self.get_ready_time_remaining_2)

            if hasattr(self, 'timer_display'):
                self.timer_display.config(text=time_text)
                # Change color based on time remaining
                if self.get_ready_time_remaining_2 <= 5:
                    self.timer_display.config(fg='red')
                elif self.get_ready_time_remaining_2 <= 10:
                    self.timer_display.config(fg='orange')
                else:
                    self.timer_display.config(fg='darkblue')

            self.get_ready_time_remaining_2 -= 1
            self.get_ready_timer_id_2 = self.root.after(1000, self.update_second_get_ready_timer)
        else:
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text="0", fg='red')
            self.on_second_get_ready_finished()

    def on_second_get_ready_finished(self):
        """Handle when second get ready timer finishes"""
        # Cancel the timer to prevent interference
        if hasattr(self, 'get_ready_timer_id_2'):
            try:
                self.root.after_cancel(self.get_ready_timer_id_2)
            except:
                pass

        print("Get ready finished! Starting second test...")
        # Start second test screen
        self.second_test_screen = SecondTestScreen(
            root=self.root,
            word_data=self.second_phase_words,
            unique_id=self.unique_id,
            personalization_flag=self.personalization_flag,
            completion_callback=self.on_second_test_completed
        )

    def skip_second_get_ready(self):
        """Skip the second get ready countdown and start test immediately"""
        # Cancel the timer
        if hasattr(self, 'get_ready_timer_id_2'):
            try:
                self.root.after_cancel(self.get_ready_timer_id_2)
            except:
                pass
        
        # Reset the time remaining to trigger the finished callback
        self.get_ready_time_remaining_2 = 0
        self.on_second_get_ready_finished()

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

        # Create footer
        self.create_footer(main_frame)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Experiment Complete - Results",
            font=("Arial", 28, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=(0, 20))

        # Create main content container with left sidebar and center content
        content_container = tk.Frame(main_frame, bg='white')
        content_container.pack(fill=tk.BOTH, expand=True)

        # Display results
        if results:
            # Left sidebar for summary (fixed width)
            summary_frame = tk.Frame(content_container, bg='lightblue', relief=tk.RAISED, bd=2, width=350)
            summary_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10), pady=0)
            summary_frame.pack_propagate(False)  # Maintain fixed width

            tk.Label(
                summary_frame,
                text="Summary Statistics",
                font=("Arial", 18, "bold"),
                bg='lightblue'
            ).pack(pady=10)

            # First Test Results
            first_test_frame = tk.Frame(summary_frame, bg='white', relief=tk.SOLID, bd=1)
            first_test_frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(
                first_test_frame,
                text="First Test:",
                font=("Arial", 12, "bold"),
                bg='white',
                fg='darkgreen' if results['first_percentage'] >= 50 else 'darkred'
            ).pack(pady=2)
            
            tk.Label(
                first_test_frame,
                text=f"{results['first_correct']} correct\n{results['first_incorrect']} incorrect\n{results['first_no_answer']} no answer",
                font=("Arial", 11),
                bg='white',
                fg='black'
            ).pack(pady=2)
            
            tk.Label(
                first_test_frame,
                text=f"{results['first_percentage']:.1f}%",
                font=("Arial", 14, "bold"),
                bg='white',
                fg='darkgreen' if results['first_percentage'] >= 50 else 'darkred'
            ).pack(pady=2)

            # Second Test Results
            second_test_frame = tk.Frame(summary_frame, bg='white', relief=tk.SOLID, bd=1)
            second_test_frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(
                second_test_frame,
                text="Second Test:",
                font=("Arial", 12, "bold"),
                bg='white',
                fg='darkgreen' if results['second_percentage'] >= 50 else 'darkred'
            ).pack(pady=2)
            
            tk.Label(
                second_test_frame,
                text=f"{results['second_correct']} correct\n{results['second_incorrect']} incorrect\n{results['second_no_answer']} no answer",
                font=("Arial", 11),
                bg='white',
                fg='black'
            ).pack(pady=2)
            
            tk.Label(
                second_test_frame,
                text=f"{results['second_percentage']:.1f}%",
                font=("Arial", 14, "bold"),
                bg='white',
                fg='darkgreen' if results['second_percentage'] >= 50 else 'darkred'
            ).pack(pady=2)

            # Overall Results
            overall_frame = tk.Frame(summary_frame, bg='white', relief=tk.SOLID, bd=1)
            overall_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

            tk.Label(
                overall_frame,
                text="Overall:",
                font=("Arial", 14, "bold"),
                bg='white',
                fg='blue'
            ).pack(pady=2)
            
            tk.Label(
                overall_frame,
                text=f"{results['total_correct']} correct\n{results['total_incorrect']} incorrect\n{results['total_no_answer']} no answer\n(out of {results['total_answered']})",
                font=("Arial", 12),
                bg='white',
                fg='black'
            ).pack(pady=2)
            
            tk.Label(
                overall_frame,
                text=f"{results['overall_percentage']:.1f}%",
                font=("Arial", 16, "bold"),
                bg='white',
                fg='blue'
            ).pack(pady=2)

            # Right side: Detailed Results with scrollbar
            results_container = tk.Frame(content_container, bg='white')
            results_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # Create canvas with scrollbar for detailed results
            canvas = tk.Canvas(results_container, bg='white')
            scrollbar = ttk.Scrollbar(results_container, orient=tk.VERTICAL, command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg='white')

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Detailed Results Section - Side by Side
            details_frame = tk.Frame(scrollable_frame, bg='white')
            details_frame.pack(pady=10, padx=20)

            tk.Label(
                details_frame,
                text="Detailed Results - All Answers",
                font=("Arial", 16, "bold"),
                bg='white'
            ).pack(pady=10)

            # Create container for two columns
            columns_container = tk.Frame(details_frame, bg='white')
            columns_container.pack(pady=5)

            # First Test Column (Left)
            first_column = tk.Frame(columns_container, bg='white', relief=tk.SOLID, bd=1)
            first_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

            tk.Label(
                first_column,
                text="First Test Answers",
                font=("Arial", 12, "bold"),
                bg='lightblue',
                pady=5
            ).pack(fill=tk.X)

            # Display all first test details
            if results['first_details']:
                for detail in results['first_details']:
                    # Determine color and status based on answer
                    if detail.get('is_empty', False):
                        color = 'lightyellow'
                        status = '○'
                    elif detail['correct']:
                        color = 'lightgreen'
                        status = '✓'
                    else:
                        color = 'lightcoral'
                        status = '✗'
                    
                    # Show answer and correct translation
                    if detail['correct']:
                        text = f"{status} {detail['ice']} → {detail['answer']}"
                    elif detail.get('is_empty', False):
                        text = f"{status} {detail['ice']}\n   Your answer: (no answer)\n   Correct: {detail['eng']}"
                    else:
                        text = f"{status} {detail['ice']}\n   Your answer: {detail['answer']}\n   Correct: {detail['eng']}"

                    detail_label = tk.Label(
                        first_column,
                        text=text,
                        font=("Arial", 9),
                        bg=color,
                        anchor='w',
                        padx=10,
                        pady=3,
                        justify=tk.LEFT
                    )
                    detail_label.pack(fill=tk.X, padx=2, pady=1)
            else:
                tk.Label(
                    first_column,
                    text="No answers recorded",
                    font=("Arial", 10, "italic"),
                    bg='white',
                    fg='gray'
                ).pack(pady=10)

            # Second Test Column (Right)
            second_column = tk.Frame(columns_container, bg='white', relief=tk.SOLID, bd=1)
            second_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

            tk.Label(
                second_column,
                text="Second Test Answers",
                font=("Arial", 12, "bold"),
                bg='lightblue',
                pady=5
            ).pack(fill=tk.X)

            # Display all second test details
            if results['second_details']:
                for detail in results['second_details']:
                    # Determine color and status based on answer
                    if detail.get('is_empty', False):
                        color = 'lightyellow'
                        status = '○'
                    elif detail['correct']:
                        color = 'lightgreen'
                        status = '✓'
                    else:
                        color = 'lightcoral'
                        status = '✗'
                    
                    # Show answer and correct translation
                    if detail['correct']:
                        text = f"{status} {detail['ice']} → {detail['answer']}"
                    elif detail.get('is_empty', False):
                        text = f"{status} {detail['ice']}\n   Your answer: (no answer)\n   Correct: {detail['eng']}"
                    else:
                        text = f"{status} {detail['ice']}\n   Your answer: {detail['answer']}\n   Correct: {detail['eng']}"

                    detail_label = tk.Label(
                        second_column,
                        text=text,
                        font=("Arial", 9),
                        bg=color,
                        anchor='w',
                        padx=10,
                        pady=3,
                        justify=tk.LEFT
                    )
                    detail_label.pack(fill=tk.X, padx=2, pady=1)
            else:
                tk.Label(
                    second_column,
                    text="No answers recorded",
                    font=("Arial", 10, "italic"),
                    bg='white',
                    fg='gray'
                ).pack(pady=10)

            # Data saved message
            tk.Label(
                scrollable_frame,
                text=f"\nData saved to: {results['csv_file']}",
                font=("Arial", 10, "italic"),
                bg='white',
                fg='gray'
            ).pack(pady=10)

            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        else:
            # Error message if results couldn't be calculated
            error_label = tk.Label(
                content_container,
                text="Error calculating results.\nPlease check the data file.",
                font=("Arial", 16),
                bg='white',
                fg='red'
            )
            error_label.pack(pady=50, expand=True)

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
            data_dir = "data"
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
            first_incorrect = 0
            first_no_answer = 0
            first_answered = 0
            second_correct = 0
            second_incorrect = 0
            second_no_answer = 0
            second_answered = 0

            # Create dictionaries to store answers by word_id for both tests
            first_test_answers = {}  # word_id -> answer
            second_test_answers = {}  # word_id -> answer

            first_details = []
            second_details = []

            # Process each row from CSV and store answers by word_id
            for _, row in df.iterrows():
                answer_raw = row.get('answer', '')
                
                # Handle empty/null answers and "none" as no answer
                if pd.isna(answer_raw) or answer_raw == '' or str(answer_raw).strip().lower() == 'none':
                    answer = ''
                    answer_display = '(no answer)'
                else:
                    answer = str(answer_raw).strip().lower()
                    answer_display = str(answer_raw).strip()
                
                # Get word_id and test_id
                word_id = row.get('word_id', '')
                test_id_raw = row.get('test_id', '')
                if pd.isna(test_id_raw):
                    continue
                test_id = str(int(float(test_id_raw))) if test_id_raw != '' else ''

                # Store the answer by word_id and test_id
                if test_id == '0':
                    first_test_answers[word_id] = {
                        'answer': answer,
                        'answer_display': answer_display,
                        'ice': row.get('ice', ''),
                        'eng': str(row.get('eng', '')).strip().lower()
                    }
                elif test_id == '1':
                    second_test_answers[word_id] = {
                        'answer': answer,
                        'answer_display': answer_display,
                        'ice': row.get('ice', ''),
                        'eng': str(row.get('eng', '')).strip().lower()
                    }

            # Now process all words from first phase
            for _, word_row in self.first_phase_words.iterrows():
                word_id = word_row['word_id']
                ice_word = word_row['ice']
                eng_word = str(word_row['eng']).strip().lower()
                
                # Check if this word was answered in the CSV
                if word_id in first_test_answers:
                    answer_data = first_test_answers[word_id]
                    answer = answer_data['answer']
                    answer_display = answer_data['answer_display']
                else:
                    # Word was not answered at all
                    answer = ''
                    answer_display = '(no answer)'
                
                # Determine correctness
                is_empty = (answer == '')
                is_correct = (answer == eng_word and answer != '')
                
                if is_empty:
                    first_no_answer += 1
                elif is_correct:
                    first_correct += 1
                    first_answered += 1
                else:
                    first_incorrect += 1
                    first_answered += 1
                
                first_details.append({
                    'ice': ice_word,
                    'eng': word_row['eng'],
                    'answer': answer_display,
                    'correct': is_correct,
                    'is_empty': is_empty
                })

            # Now process all words from second phase
            for _, word_row in self.second_phase_words.iterrows():
                word_id = word_row['word_id']
                ice_word = word_row['ice']
                eng_word = str(word_row['eng']).strip().lower()
                
                # Check if this word was answered in the CSV
                if word_id in second_test_answers:
                    answer_data = second_test_answers[word_id]
                    answer = answer_data['answer']
                    answer_display = answer_data['answer_display']
                else:
                    # Word was not answered at all
                    answer = ''
                    answer_display = '(no answer)'
                
                # Determine correctness
                is_empty = (answer == '')
                is_correct = (answer == eng_word and answer != '')
                
                if is_empty:
                    second_no_answer += 1
                elif is_correct:
                    second_correct += 1
                    second_answered += 1
                else:
                    second_incorrect += 1
                    second_answered += 1
                
                second_details.append({
                    'ice': ice_word,
                    'eng': word_row['eng'],
                    'answer': answer_display,
                    'correct': is_correct,
                    'is_empty': is_empty
                })

            # Fixed: Always use 25 as the total for each test (this is how many words are tested)
            first_total = 25
            second_total = 25

            # Calculate percentages based on 25 questions each
            first_percentage = (first_correct / first_total * 100) if first_total > 0 else 0
            second_percentage = (second_correct / second_total * 100) if second_total > 0 else 0
            total_correct = first_correct + second_correct
            total_incorrect = first_incorrect + second_incorrect
            total_no_answer = first_no_answer + second_no_answer
            overall_percentage = (total_correct / 50 * 100)  # Out of 50 total (25+25)

            results = {
                'first_correct': first_correct,
                'first_incorrect': first_incorrect,
                'first_no_answer': first_no_answer,
                'first_total': first_total,
                'first_percentage': first_percentage,
                'second_correct': second_correct,
                'second_incorrect': second_incorrect,
                'second_no_answer': second_no_answer,
                'second_total': second_total,
                'second_percentage': second_percentage,
                'total_correct': total_correct,
                'total_incorrect': total_incorrect,
                'total_no_answer': total_no_answer,
                'total_answered': 50,  # Always 50 (25 + 25)
                'overall_percentage': overall_percentage,
                'first_details': first_details,
                'second_details': second_details,
                'csv_file': latest_csv
            }

            print("Results calculated:")
            print(f"  First Test: {first_correct} correct, {first_incorrect} incorrect, {first_no_answer} no answer")
            print(f"  Second Test: {second_correct} correct, {second_incorrect} incorrect, {second_no_answer} no answer")
            print(f"  Overall: {total_correct}/50 ({overall_percentage:.1f}%)")

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

        # Create footer
        self.create_footer(main_frame)

        # Top bar with title and Next button
        top_bar = tk.Frame(main_frame, bg='white')
        top_bar.pack(fill=tk.X, pady=(0, 30))

        # Title on the left
        title_label = tk.Label(
            top_bar,
            text="Break Time",
            font=("Arial", 32, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(side=tk.LEFT)

        # Next button on the right
        next_button = tk.Button(
            top_bar,
            text="Next",
            font=("Arial", 14),
            bg='lightgreen',
            command=self.on_break_next_clicked,
            width=10,
            height=2
        )
        next_button.pack(side=tk.RIGHT)

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

    def on_break_next_clicked(self):
        """Handle next button click from break screen"""
        print("Break completed, moving to second memorizing screen")
        # Show second memorizing screen before the second test
        self.show_second_memorizing_screen()

    def show_second_memorizing_screen(self):
        """Display the second memorizing screen with word pairs before the second test"""
        # Cancel any existing timers to prevent conflicts
        if hasattr(self, 'break_timer_id'):
            try:
                self.root.after_cancel(self.break_timer_id)
            except:
                pass
        if hasattr(self, 'timer_id'):
            try:
                self.root.after_cancel(self.timer_id)
            except:
                pass
        if hasattr(self, 'first_timer_id'):
            try:
                self.root.after_cancel(self.first_timer_id)
            except:
                pass

        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main container
        main_container = tk.Frame(self.root, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create footer
        self.create_footer(main_container)

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
            font=("Arial", 16, "bold"),
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
                padx=0,
                pady=0
            )
            pair_frame.pack(padx=0, pady=0)

            # Number label (smaller)
            number_label = tk.Label(
                pair_frame,
                text=f"{index + 1}.",
                font=("Arial", 12, "bold"),
                bg='white',
                fg='black',
                width=2,
                anchor='e'
            )
            number_label.pack(side=tk.LEFT, padx=(0, 3))

            # Icelandic word (centered, right-aligned)
            ice_label = tk.Label(
                pair_frame,
                text=ice_word,
                font=("Arial", 16, "bold"),
                bg='white',
                fg='black',
                relief=tk.FLAT,
                padx=3,
                pady=0,
                width=18,
                anchor='e'
            )
            ice_label.pack(side=tk.LEFT, padx=1)

            # Arrow (bigger and centered)
            arrow_label = tk.Label(
                pair_frame,
                text="→",
                font=("Arial", 16, "bold"),
                bg='white',
                fg='darkblue',
                width=2
            )
            arrow_label.pack(side=tk.LEFT, padx=5)

            # English word (centered, left-aligned)
            eng_label = tk.Label(
                pair_frame,
                text=eng_word,
                font=("Arial", 16, "bold"),
                bg='white',
                fg='black',
                relief=tk.FLAT,
                padx=3,
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
            text="04:00",  # Changed from "08:00" to "04:00"
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

        After the time expires, you will be tested again on your remembrance of these word pairs.

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
            fg='black',
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
