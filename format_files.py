'''
DESCRIPTION
Format files for the project
NOTES
This script is used to format files for the project. These might be JSON files or converting files to different formats.
Version:        0.1
Author:         Tim Haintz                         
Creation Date:  18/3/2024
LINKS
EXAMPLE USAGE
python format_files.py -input_file data.json -output_file output_file.json -format json
python format_files.py -input_directory input_folder -output_directory output_file  -format json
python format_files.py -input_directory input_folder -output_directory output_file  -format json_categorisation
'''
# Import the required libraries
import argparse
import json
import glob

import json
import glob

def format_categorisation_json_files(input_directory=None, input_file=None, output_file=None):
    # Initialize an empty list to hold all the data
    all_data = []

    # Check if input_directory is provided
    if input_directory:
        # Get a list of all JSON files in the specified directory
        json_files = glob.glob(input_directory + '/*.json')

        for file_name in json_files:
            with open(file_name, 'r', encoding='utf-8') as f:
                # Load file content as a string
                print(file_name)
                file_content = f.read()
                # Parse the string into JSON
                data = json.loads(json.loads(file_content))

                # Check if data is a dictionary
                if isinstance(data, dict):
                    # Extract the desired properties from each object
                    for key, values in data.items():
                        for value in values:
                            all_data.append({
                                'PE_ID': value.get('PE_ID'),
                                'Category': value.get('Category'),
                                'Prompt_Example': value.get('Prompt_Example'),
                                'Reasoning': value.get('Reasoning')
                            })

    elif input_file:
        with open(input_file, 'r', encoding='utf-8') as f:
            # Load file content as a string
            file_content = f.read()
            # Parse the string into JSON
            data = json.loads(json.loads(file_content))

            # Check if data is a dictionary
            if isinstance(data, dict):
                # Extract the desired properties from each object
                for key, values in data.items():
                    for value in values:
                        all_data.append({
                            'PE_ID': value.get('PE_ID'),
                            'Category': value.get('Category'),
                            'Prompt_Example': value.get('Prompt_Example'),
                            'Reasoning': value.get('Reasoning')
                        })

    # Write the output to the specified output file
    with open(output_file, 'w') as f:
        json.dump(all_data, f, indent=4)

#############
# MAIN CODE #
#############
if __name__ == '__main__':
    # Add the arguments
    parser = argparse.ArgumentParser(description='Format files for the project')
    parser.add_argument('-input_directory', type=str, help='The input directory to format. Will format all files in the directory')
    parser.add_argument('-input_file', type=str, help='The input file to format. Will format a single file.')
    parser.add_argument('-output_file', type=str,
                        default='./output.json',
                        help='The output file to write to. Default is ./output.json')
    parser.add_argument('-format', choices=['json', 'json_categorisation'], 
                        default='json',
                        help='Convert JSON string to pretty JSON. Default is json.')

    args = parser.parse_args()

try:
    if args.input_file:
        if args.format == 'json':
            print(f"Opening file: {args.input_file}")  # Add this line
            with open(args.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            with open(args.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        elif args.format == 'json_categorisation':
            print(f"Opening file: {args.input_file}")  # Add this line
            format_categorisation_json_files(input_file=args.input_file, output_file=args.output_file)
    elif args.format == 'json_categorisation':
        print(f"Opening directory: {args.input_directory}")  # Add this line
        format_categorisation_json_files(input_directory=args.input_directory, output_file=args.output_file)
except UnicodeDecodeError:
    print(f"Error opening file or directory")
    raise