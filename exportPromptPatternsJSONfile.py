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
                f.write('<p>URL: <a href="{}">{}</a></p>\n'.format(title['URLReference'], title['URLReference']))
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

def count_prompt_patterns(data):
    title_counts = {}
    total_title_count = 0
    total_category_count = 0
    total_pattern_count = 0
    total_example_count = 0
    for title in data['Source']['Titles']:
        title_count = 1
        category_count = 0
        pattern_count = 0
        example_count = 0
        for category in title['CategoriesAndPatterns']:
            category_count += 1
            for pattern in category['PromptPatterns']:
                pattern_count += 1
                example_count += len(pattern['ExamplePrompts'])
            title_count += 1
        title_counts[title['Title']] = (title_count - 1, category_count, pattern_count, example_count)
        total_title_count += 1
        total_category_count += category_count
        total_pattern_count += pattern_count
        total_example_count += example_count
    return title_counts, (total_title_count, total_category_count, total_pattern_count, total_example_count)

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Export prompt patterns from JSON file.')
parser.add_argument('--count', action='store_true', help='count the number of Titles, PatternCategory, and pattern name')
parser.add_argument('--format', choices=['console', 'html'], default='console', help='output format (default: console)')
parser.add_argument('--filename', default='promptpatterns.html', help='output filename (default: promptpatterns.html)')
parser.add_argument('--show-examples', action='store_true', help='show examples of how to use this script')
args = parser.parse_args()

# Check if the --show-examples argument is present
if args.show_examples:
    # Print the help section with examples
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
    print('To count the number of Titles, PatternCategory, and pattern name, run the following command:')
    print('python exportPromptPatternsJSONfile.py --count')
elif args.count:
    # Read the prompt patterns from the JSON file
    data = read_prompt_patterns()

    # Count the number of Titles, PatternCategory, and pattern name
    title_counts, total_counts = count_prompt_patterns(data)
    for title, counts in title_counts.items():
        print('Title:', title)
        print('\tTotal Pattern Categories:', counts[1])
        print('\tTotal Patterns:', counts[2])
        print('\tTotal Example Prompts:', counts[3])
    print('Total Titles:', total_counts[0])
    print('Total Pattern Categories:', total_counts[1])
    print('Total Patterns:', total_counts[2])
    print('Total Example Prompts:', total_counts[3])
else:
    # Read the prompt patterns from the JSON file
    data = read_prompt_patterns()

    # Write the prompt patterns to the specified format and filename
    write_prompt_patterns(data, args.format, args.filename)
