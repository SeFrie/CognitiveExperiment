WARNING: The path to the .xlsx is different in PyCharm and VS Code. The two paths we have used is shown below. 
To distinguish the two, we have used single quotations signs for PyCharm and double for VS Code

PyCharm:
def load_word_data(self):
    """Load word data from Excel file"""
    try:
        df = pd.read_excel('word_pairs/Icelandic_English_Danish_words.xlsx')

VS Code:
def load_word_data(self):
    """Load word data from Excel file"""
    try:
        df = pd.read_excel("word_pairs/Icelandic_English_Danish_words.xlsx")
