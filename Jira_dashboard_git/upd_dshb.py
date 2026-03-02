import re

# Define the names of the input and output files
html_template_path = 'audio_missing_25_11.html'
new_csv_data_path = 'JIRA.csv'
output_html_path = 'updated_dashboard.html'

print("Starting dashboard update process...")

# Mapping of French abbreviations (stripped of dots) to English months
month_map = {
    "janv": "Jan", "févr": "Feb", "mars": "Mar", "avr": "Apr", "mai": "May", "juin": "Jun",
    "juil": "Jul", "août": "Aug", "sept": "Sep", "oct": "Oct", "nov": "Nov", "déc": "Dec"
}

try:
    # 1. Read the new CSV data from the provided file
    with open(new_csv_data_path, 'r', encoding='utf-8') as f:
        # Read all lines to parse the content and the first data row
        lines = f.readlines()
        new_csv_content = "".join(lines).strip()

        # Parse the latest date from the first data row (index 1)
        new_month_year = None
        if len(lines) > 1:
            first_row = lines[1]
            try:
                # Format example: "27/janv./26 10:07 AM;..."
                # Extract "27/janv./26"
                date_part = first_row.split(';')[0].split(' ')[0] 
                parts = date_part.split('/')
                
                if len(parts) >= 3:
                    # parts[1] is e.g. "janv."
                    raw_month = parts[1].lower().replace('.', '')
                    year_suffix = parts[2]
                    year = "20" + year_suffix
                    
                    if raw_month in month_map:
                        english_month = month_map[raw_month]
                        new_month_year = f"{english_month} {year}"
                        print(f"Detected latest date from CSV: {new_month_year}")
                    else:
                        print(f"Warning: Could not map month '{raw_month}'")
            except Exception as parse_err:
                print(f"Warning: Could not parse date from first row: {parse_err}")
                
    print(f"Successfully read new data from '{new_csv_data_path}'.")

    # 2. Read the existing HTML template
    with open(html_template_path, 'r', encoding='utf-8') as f:
        html_template = f.read()
    print(f"Successfully read the HTML template from '{html_template_path}'.")

    # 3. Use regular expressions to find and replace the old CSV data
    pattern = r"(const csvContent = `)[\s\S]*?(`;)"
    
    def replace_csv_content(match):
        return f"{match.group(1)}{new_csv_content}{match.group(2)}"

    updated_html, num_replacements = re.subn(pattern, replace_csv_content, html_template, count=1, flags=re.DOTALL)

    if num_replacements > 0:
        print("Found the data block in the HTML and replaced it with the new content.")
        
        # 4. Update the Title and Header if a new date was parsed
        if new_month_year:
            # Update <title>Jira Insights - Dec 2025</title>
            # Matches "Jira Insights - [Anything]" and replaces the end part
            updated_html = re.sub(r"(<title>Jira Insights - ).+?(</title>)", f"\\1{new_month_year}\\2", updated_html)
            
            # Update <h2>... Data Overview (Sept - Dec 2025)</h2>
            # Matches "Data Overview (... - [Anything])"
            updated_html = re.sub(r"(Data Overview \(.* - ).+?(\))", f"\\1{new_month_year}\\2", updated_html)
            
            print(f"Updated dashboard title and header to end with '{new_month_year}'.")

        # 5. Write the modified content to a new HTML file
        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(updated_html)
        print(f"Success! The updated dashboard has been saved as '{output_html_path}'.")
    else:
        print("Error: Could not find the 'const csvContent' data block in the HTML template.")

except FileNotFoundError as e:
    print(f"Error: File not found - {e}. Please ensure all files are in the same directory.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
