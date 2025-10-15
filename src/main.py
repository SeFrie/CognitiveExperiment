import tkinter as tk
from tkinter import ttk
import pandas as pd
import csv
import uuid
import os
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

        # Show welcome screen
        self.show_welcome_screen()

    def load_word_data(self):
        """Load word data from Excel file"""
        try:
            df = pd.read_excel('word_pairs/dummy_words.xlsx')
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
                    # Assume first column is word_id, second is Icelandic, third is English
                    if len(df.columns) >= 3:
                        word_id_col = df.columns[0]
                        ice_col = df.columns[1]
                        eng_col = df.columns[2]
                    else:
                        # Only 2 columns, assume they are Icelandic and English
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
        filename = f"data/experiment_{self.unique_id}_{timestamp}.csv"

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
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = tk.Label(
            main_container,
            text="Memorizing Screen",
            font=("Arial", 20, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=(0, 10))

        # Create horizontal layout: word grid on left, info panel on right
        content_frame = tk.Frame(main_container, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left side: Word pairs grid (5 columns x 4 rows)
        grid_frame = tk.Frame(content_frame, bg='white', relief=tk.RAISED, bd=1)
        grid_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Grid title
        grid_title = tk.Label(
            grid_frame,
            text="Word Pairs",
            font=("Arial", 16, "bold"),
            bg='white',
            fg='black'
        )
        grid_title.pack(pady=10)

        # Create the word grid
        word_grid_frame = tk.Frame(grid_frame, bg='white')
        word_grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Display word pairs in 5x4 grid (20 pairs total)
        self.display_word_grid(word_grid_frame)

        # Right side: Information panel and timer
        info_panel = tk.Frame(content_frame, bg='lightgray', width=300, relief=tk.RAISED, bd=1)
        info_panel.pack(side=tk.RIGHT, fill=tk.Y)
        info_panel.pack_propagate(False)  # Maintain fixed width

        # Timer display
        timer_frame = tk.Frame(info_panel, bg='lightgray')
        timer_frame.pack(fill=tk.X, padx=10, pady=10)

        timer_label = tk.Label(
            timer_frame,
            text="Time Remaining:",
            font=("Arial", 12, "bold"),
            bg='lightgray',
            fg='black'
        )
        timer_label.pack()

        self.timer_display = tk.Label(
            timer_frame,
            text="08:00",
            font=("Arial", 24, "bold"),
            bg='lightgray',
            fg='red'
        )
        self.timer_display.pack()

        # Information text area
        info_title = tk.Label(
            info_panel,
            text="Instructions",
            font=("Arial", 14, "bold"),
            bg='lightgray',
            fg='black'
        )
        info_title.pack(pady=(10, 5))

        # Create scrollable text widget for information
        text_frame = tk.Frame(info_panel, bg='lightgray')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        info_text = tk.Text(
            text_frame,
            font=("Arial", 10),
            bg='white',
            fg='black',
            wrap=tk.WORD,
            height=10
        )

        info_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=info_text.yview)
        info_text.configure(yscrollcommand=info_scrollbar.set)

        info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add dummy instruction text
        instruction_text = """
        Study the word pairs carefully. You have 8 minutes to memorize the associations between the Icelandic and English words.

        After the time expires, you will be tested on your remembrance of these word pairs.

        Good luck with your memorization!
        """

        info_text.insert(tk.END, instruction_text.strip())
        info_text.config(state=tk.DISABLED)

        # Add a Next button for testing purposes
        next_button_frame = tk.Frame(info_panel, bg='lightgray')
        next_button_frame.pack(fill=tk.X, padx=10, pady=10)

        next_button = tk.Button(
            next_button_frame,
            text="Next (Testing)",
            font=("Arial", 12),
            bg='orange',
            fg='white',
            command=self.on_timer_finished,  # Use the same function as timer completion
            width=15,
            height=2
        )
        next_button.pack()

        # Start the countdown timer
        self.start_countdown_timer()

    def display_word_grid(self, parent_frame):
        """Display word pairs in a 5x4 grid"""
        # Ensure we have enough word pairs (pad with empty if needed)
        word_pairs = []
        for index, row in self.word_data.iterrows():
            ice_word = row.get('ice', '')
            eng_word = row.get('eng', '')
            if ice_word and eng_word:
                word_pairs.append((ice_word, eng_word))

        # Pad to exactly 20 pairs if needed
        while len(word_pairs) < 20:
            word_pairs.append(('', ''))

        # Create 4 rows x 5 columns grid
        for row in range(4):
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
                        font=("Arial", 12, "bold"),
                        bg='lightblue',
                        fg='black',
                        relief=tk.FLAT,
                        padx=5,
                        pady=3
                    )
                    ice_label.pack(fill=tk.X)

                    # English word (bottom)
                    eng_label = tk.Label(
                        pair_frame,
                        text=eng_word,
                        font=("Arial", 12),
                        bg='lightgreen',
                        fg='black',
                        relief=tk.FLAT,
                        padx=5,
                        pady=3
                    )
                    eng_label.pack(fill=tk.X)

        # Configure grid weights for equal distribution
        for i in range(4):
            parent_frame.grid_rowconfigure(i, weight=1)
        for i in range(5):
            parent_frame.grid_columnconfigure(i, weight=1)

    def start_countdown_timer(self):
        """Start the 8-minute countdown timer"""
        self.time_remaining = 8 * 60  # 8 minutes in seconds
        self.update_timer()

    def update_timer(self):
        """Update the countdown timer display"""
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
            self.root.after(1000, self.update_timer)
        else:
            # Time's up!
            if hasattr(self, 'timer_display'):
                self.timer_display.config(text="00:00", fg='red')
            self.on_timer_finished()

    def on_timer_finished(self):
        """Handle when the countdown timer reaches zero"""
        print("Memorization time finished!")
        # Use the new TestScreen module
        self.test_screen = TestScreen(
            root=self.root,
            word_data=self.word_data,
            unique_id=self.unique_id,
            completion_callback=self.on_test_completed
        )

    def on_test_completed(self, answers):
        """Handle test completion"""
        print(f"Test completed with {len(answers)} answers")

        # Show break screen instead of completion message
        self.show_break_screen()

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

        You have now finished the first memory test. Take a moment to relax and rest your mind.

        During this break, you can:
        • Take a deep breath and relax
        • Stretch if you need to
        • Clear your mind from the previous task

        The next part of the experiment will begin when you click the "Next" button below.

        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

        Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

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
        print("Break completed, moving to second test")
        # Move to second test screen instead of completion
        self.show_second_test_screen()

    def show_second_test_screen(self):
        """Display the second test screen with randomized questions"""
        print("Starting second test with randomized questions!")
        # Create second test screen with randomized question order
        self.second_test_screen = SecondTestScreen(
            root=self.root,
            word_data=self.word_data,
            unique_id=self.unique_id,
            completion_callback=self.on_second_test_completed
        )

    def on_second_test_completed(self, answers):
        """Handle second test completion"""
        print(f"Second test completed with {len(answers)} answers")
        # Calculate scores and show final completion screen with results
        self.calculate_and_show_results()

    def calculate_and_show_results(self):
        """Calculate test scores and show results on final screen"""
        try:
            # Find the most recent CSV file for this session
            data_dir = "../data"
            csv_files = [f for f in os.listdir(data_dir) if f.startswith(f"experiment_{self.unique_id}") and f.endswith('.csv')]

            if csv_files:
                csv_files.sort()
                latest_csv = os.path.join(data_dir, csv_files[-1])
                df = pd.read_csv(latest_csv)

                # Calculate scores for both tests
                first_test_correct = 0
                second_test_correct = 0
                total_questions = len(df)

                for index, row in df.iterrows():
                    correct_answer = str(row['eng']).lower().strip()

                    # Check first test answer (answ_1)
                    first_answer = str(row['answ_1']).lower().strip() if pd.notna(row['answ_1']) else ''
                    if first_answer == correct_answer:
                        first_test_correct += 1

                    # Check second test answer (answ_2)
                    second_answer = str(row['answ_2']).lower().strip() if pd.notna(row['answ_2']) else ''
                    if second_answer == correct_answer:
                        second_test_correct += 1

                # Calculate percentages
                first_test_percentage = (first_test_correct / total_questions) * 100 if total_questions > 0 else 0
                second_test_percentage = (second_test_correct / total_questions) * 100 if total_questions > 0 else 0

                print(f"First test: {first_test_correct}/{total_questions} ({first_test_percentage:.1f}%)")
                print(f"Second test: {second_test_correct}/{total_questions} ({second_test_percentage:.1f}%)")

                # Show results screen
                self.show_results_screen(first_test_correct, second_test_correct, total_questions,
                                       first_test_percentage, second_test_percentage)
            else:
                print("No CSV file found for scoring")
                self.show_final_completion_screen()

        except Exception as e:
            print(f"Error calculating results: {e}")
            self.show_final_completion_screen()

    def show_results_screen(self, first_correct, second_correct, total_questions, first_percentage, second_percentage):
        """Show the results screen"""
        # Clear the root window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create main frame
        main_frame = tk.Frame(self.root, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)

        # Title
        title_label = tk.Label(
            main_frame,
            text="Experiment Results",
            font=("Arial", 32, "bold"),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=(0, 40))

        # Results container
        results_frame = tk.Frame(main_frame, bg='white')
        results_frame.pack(expand=True)

        # First test results
        first_test_frame = tk.Frame(results_frame, bg='lightblue', relief=tk.RAISED, bd=3, padx=20, pady=20)
        first_test_frame.pack(fill=tk.X, pady=(0, 20))

        first_test_title = tk.Label(
            first_test_frame,
            text="First Test Results",
            font=("Arial", 20, "bold"),
            bg='lightblue',
            fg='black'
        )
        first_test_title.pack()

        first_test_score = tk.Label(
            first_test_frame,
            text=f"Correct Answers: {first_correct} out of {total_questions}",
            font=("Arial", 16),
            bg='lightblue',
            fg='black'
        )
        first_test_score.pack(pady=5)

        first_test_percentage_label = tk.Label(
            first_test_frame,
            text=f"Score: {first_percentage:.1f}%",
            font=("Arial", 18, "bold"),
            bg='lightblue',
            fg='darkgreen' if first_percentage >= 70 else 'darkorange' if first_percentage >= 50 else 'darkred'
        )
        first_test_percentage_label.pack(pady=5)

        # Second test results
        second_test_frame = tk.Frame(results_frame, bg='lightgreen', relief=tk.RAISED, bd=3, padx=20, pady=20)
        second_test_frame.pack(fill=tk.X, pady=(0, 20))

        second_test_title = tk.Label(
            second_test_frame,
            text="Second Test Results (Randomized)",
            font=("Arial", 20, "bold"),
            bg='lightgreen',
            fg='black'
        )
        second_test_title.pack()

        second_test_score = tk.Label(
            second_test_frame,
            text=f"Correct Answers: {second_correct} out of {total_questions}",
            font=("Arial", 16),
            bg='lightgreen',
            fg='black'
        )
        second_test_score.pack(pady=5)

        second_test_percentage_label = tk.Label(
            second_test_frame,
            text=f"Score: {second_percentage:.1f}%",
            font=("Arial", 18, "bold"),
            bg='lightgreen',
            fg='darkgreen' if second_percentage >= 70 else 'darkorange' if second_percentage >= 50 else 'darkred'
        )
        second_test_percentage_label.pack(pady=5)

        # Overall comparison
        comparison_frame = tk.Frame(results_frame, bg='lightyellow', relief=tk.RAISED, bd=3, padx=20, pady=20)
        comparison_frame.pack(fill=tk.X)

        comparison_title = tk.Label(
            comparison_frame,
            text="Performance Comparison",
            font=("Arial", 18, "bold"),
            bg='lightyellow',
            fg='black'
        )
        comparison_title.pack()

        # Calculate difference
        difference = second_percentage - first_percentage
        if difference > 0:
            comparison_text = f"Improvement: +{difference:.1f}% better in second test"
            comparison_color = 'darkgreen'
        elif difference < 0:
            comparison_text = f"Decline: {difference:.1f}% lower in second test"
            comparison_color = 'darkred'
        else:
            comparison_text = "Same performance in both tests"
            comparison_color = 'black'

        comparison_label = tk.Label(
            comparison_frame,
            text=comparison_text,
            font=("Arial", 14, "bold"),
            bg='lightyellow',
            fg=comparison_color
        )
        comparison_label.pack(pady=5)

        # Thank you message
        thank_you_label = tk.Label(
            main_frame,
            text="Thank you for your participation!",
            font=("Arial", 18, "bold"),
            bg='white',
            fg='black'
        )
        thank_you_label.pack(pady=(30, 0))

def main():
    root = tk.Tk()
    app = ExperimentApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
