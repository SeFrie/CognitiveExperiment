# Group 10 - final project
## Memory Consolidation under the influence of Social Media

This study evaluates how the memory is influenced by Social Media usage. In this repository you'll find the main experimental script (src/main), the obtained data (sr as well as the statistical analysis (src/statistical_analysis) from the condcted study.

## Downloading the code

The path to the .xlsx is different in PyCharm and VS Code. The two paths we have used is shown below. 
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
