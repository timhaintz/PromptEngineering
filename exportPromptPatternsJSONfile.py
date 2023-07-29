'''
DESCRIPTION
Export the prompt patterns from the promptpatterns.json JSON file.
NOTES
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  26/7/2023
LINKS
EXAMPLES
1. To print the prompt patterns to the console, run the following command:

```
python exportPromptPatternsJSONfile.py --format console
```

This will print the prompt patterns to the console in a formatted way.

2. To write the prompt patterns to an HTML file with the default filename `promptpatterns.html`, run the following command:

```
python exportPromptPatternsJSONfile.py --format html
```

This will write the prompt patterns to an HTML file called `promptpatterns.html` in the same directory as the script.

3. To write the prompt patterns to an HTML file with a custom filename, run the following command:

```
python exportPromptPatternsJSONfile.py --format html --filename mypromptpatterns.html
```

This will write the prompt patterns to an HTML file called `mypromptpatterns.html` in the same directory as the script.

4. To include the current date in the filename of the HTML file, use the `{date}` placeholder in the filename argument, like this:

```
python exportPromptPatternsJSONfile.py --format html --filename promptpatterns_{date}.html
```

This will write the prompt patterns to an HTML file with a filename that includes the current date in the format `promptpatterns_YYYYmmdd.html`.

Note that you can replace `promptpatterns.html`, `mypromptpatterns.html`, or `promptpatterns_{date}.html` with any filename you like.

'''
# Import modules
import argparse
import json
import datetime

# Get the current date and time
now = datetime.datetime.now()
# Format the date as YYYYmmdd
date_str = now.strftime('%Y%m%d')

def read_prompt_patterns():
    # Open the JSON file
    with open('promptpatterns.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Return the prompt patterns
    return data

def write_prompt_patterns(data, format, filename):
    if format == 'console':
        # Print the prompt patterns to the console
        for title in data['Source']['Titles']:
            print('Title:', title['Title'])
            for category in title['CategoriesAndPatterns']:
                print('\tPattern Category:', category['PatternCategory'])
                for pattern in category['PromptPatterns']:
                    print('\t\tPattern Name:', pattern['PatternName'])
                    print('\t\tExample Prompts:')
                    for example in pattern['ExamplePrompts']:
                        print('\t\t\t', example)
                    print()
    elif format == 'html':
        if not filename.endswith('.html'):
            filename += '.html'
        if '{date}' in filename:
            # Get the current date and time
            now = datetime.datetime.now()

            # Format the date as YYYYmmdd
            date_str = now.strftime('%Y%m%d')

            # Replace {date} with the current date in the filename
            filename = filename.replace('{date}', date_str)

        # Write the prompt patterns to an HTML file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('<html>\n')
            f.write('<head>\n')
            f.write('<title>Prompt Patterns</title>\n')
            f.write('</head>\n')
            f.write('<body>\n')
            for title in data['Source']['Titles']:
                f.write('<h1>{}</h1>\n'.format(title['Title']))
                for category in title['CategoriesAndPatterns']:
                    f.write('<h2>{}</h2>\n'.format(category['PatternCategory']))
                    for pattern in category['PromptPatterns']:
                        f.write('<h3>{}</h3>\n'.format(pattern['PatternName']))
                        f.write('<ul>\n')
                        for example in pattern['ExamplePrompts']:
                            f.write('<li>{}</li>\n'.format(example))
                        f.write('</ul>\n')
            f.write('</body>\n')
            f.write('</html>\n')
    else:
        print('Invalid format:', format)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Export prompt patterns from JSON file.')
parser.add_argument('--format', choices=['console', 'html'], default='console', help='output format (default: console)')
parser.add_argument('--filename', default='promptpatterns.html', help='output filename (default: promptpatterns.html)')
args = parser.parse_args()

# Print help section with examples
print('EXAMPLES')
print('To print the prompt patterns to the console, run the following command:')
print('python exportPromptPatternsJSONfile.py --format console')
print()
print('To write the prompt patterns to an HTML file with the default filename `promptpatterns.html`, run the following command:')
print('python exportPromptPatternsJSONfile.py --format html')
print()
print('To write the prompt patterns to an HTML file with a custom filename, run the following command:')
print('python exportPromptPatternsJSONfile.py --format html --filename mypromptpatterns.html')
print()
print('To include the current date in the filename of the HTML file, use the `{date}` placeholder in the filename argument, like this:')
print('python exportPromptPatternsJSONfile.py --format html --filename promptpatterns_{date}.html')
print()

# Read the prompt patterns from the JSON file
data = read_prompt_patterns()

# Write the prompt patterns to the specified format and filename
write_prompt_patterns(data, args.format, args.filename)
