def filter_lines(file_path):
    # Read lines from the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Filter lines where the length of the line (minus the newline character) is greater than 2
    filtered_lines = [line.strip() for line in lines if len(line.strip()) > 3]

    # Write the filtered lines back to a new file
    with open('filtered_file.txt', 'w') as file:
        for line in filtered_lines:
            file.write(line + '\n')

# Replace 'your_file.txt' with the path to your text file
filter_lines('Vietnamese_transform_dict.txt')