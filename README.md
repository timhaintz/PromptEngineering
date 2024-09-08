# PromptEngineering4Cybersecurity
Prompt Engineering for Cybersecurity

This repository contains a collection of Python scripts and tools designed for various tasks related to text extraction, categorisation, and prompt engineering. The main functionalities include a JSON database of research papers with Prompt Patterns (PPs) and Prompt Examples (PEs) extracted, extracting text from PDFs, categorising text using Cosine Similarity, and generating and testing prompts for AI models.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Extract Text from PDF](#extract-text-from-pdf)
  - [Categorise Text Using Cosine Similarity](#categorise-text-using-cosine-similarity)
  - [Generate and Test Prompt](#generate-and-test-prompt)
  - [Export PPs and PEs from the JSON File](#export-pps-and-pes-from-the-json-file)
- [Directory Structure](#directory-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
```sh
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

2. Create and activate a virtual environment:
```sh
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

3. Install the required dependencies:
```sh
pip install -r requirements.txt
```

4. Set up environment variables by creating a `.env` file in the root directory and adding the necessary keys:

    ```env
    AZURE_OPENAI_MODEL=<your-model>
    API_VERSION=<your-api-version>
    AZURE_OPENAI_KEY=<your-api-key>
    AZURE_OPENAI_ENDPOINT=<your-endpoint>
    ```

## Usage

### Extract Text from PDF

To extract text from a PDF file, use the `extractTextFromPDF.py` script. Below are some examples:

```sh
python extractTextFromPDF.py -filename "Test.pdf"
python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10
python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -extractexamples True
python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -summary True
python extractTextFromPDF.py -filename "Test.pdf" -pages 1-10 -keypoints True
```

### Categorise Text Using Cosine Similarity

To categorise text using Cosine Similarity, use the categorisation_cosine_similarity.py script:

```sh
python categorisation_cosine_similarity.py --top_n 5
python categorisation_cosine_similarity.py --threshold 0.5
```

### Generate and Test Prompt

To generate and test prompts, use the testPrompts.py script:

```sh
python testPrompts.py
python vision_testPrompts.py
```

### Export PPs and PEs from the JSON File

To export and count the PPs and PEs from the `promptpatterns.json` JSON file, use the `exportPromptPatternsJSONfile.py` script.
Below are some example usages:

1. **Print the PPs and PEs to the console:**
This will print the PPs and PEs to the console in a formatted way.

```sh
python exportPromptPatternsJSONfile.py --format console
``` 

2. **Write the PPs and PEs to an HTML file with the default filename `promptpatterns.html`:**

This will write the PPs and PEs to an HTML file called `promptpatterns.html` in the same directory as the script.

```sh
python exportPromptPatternsJSONfile.py --format html
```

3. **Write the PPs and PEs to an HTML file with a custom filename:**
This will write the PPs and PEs to an HTML file called `mypromptpatterns.html` in the same directory as the script.

```sh
python exportPromptPatternsJSONfile.py --format html --filename mypromptpatterns.html
```

4. **Include the current date in the filename of the HTML file:**
This will write the PPs and PEs to an HTML file with a filename that includes the current date in the format `promptpatterns_YYYYmmdd.html`.

```sh
python exportPromptPatternsJSONfile.py --format html --filename promptpatterns_{date}.html
```

5. **Count the number of Titles, PatternCategory, and pattern name:**

This will count the number of Titles, PatternCategory, and pattern name and output it to the console.

```sh
python exportPromptPatternsJSONfile.py --count
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements, research paper additions or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.