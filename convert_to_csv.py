import re
import csv
from wikimedia import get_wikimedia_url_via_api
import subprocess
import os


# Create images directory if not exists
if not os.path.exists('images'):
    os.makedirs('images')

def download_and_convert_image(url, index):
    if not url:
        return '', ''
        
    # Download and convert original image
    full_filename = f'images/m{index}.jpg'
    small_filename = f'images/m{index}_small.jpg'
    
    try:
        # Download and convert to jpg using ImageMagick
        subprocess.run(['./magick', url, full_filename], check=True)
        
        # Create thumbnail
        subprocess.run(['./magick', full_filename, '-resize', '320x', small_filename], check=True)
        
        return full_filename, small_filename
    except subprocess.CalledProcessError:
        return '', ''

def clean_distance(text):
    # First check for numbers outside tags
    clean_text = re.sub(r'\{\{(?:ntsh|nts)\|[^}]+\}\}', '', text)  # Remove all nts/ntsh tags
    if clean_text.strip() and re.search(r'\d+\.?\d*(?:\s*[-–]\s*\d+\.?\d*)?', clean_text):
        return clean_text.strip()
    
    # If no outside numbers, check for ntsh or nts tags
    matches = re.findall(r'\{\{(?:ntsh|nts)\|([^}]+)\}\}', text)
    if matches:
        return matches[0]
    
    return ''

def clean_text(text):
    # Handle empty markers
    if text == '{{sort|z|–}}':
        return ''
    
    # Remove HTML tags and special Wiki markup
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\{\{sort\|[^}]+\|([^}]+)\}\}', r'\1', text)  # Handle {{sort|x|y}} format
    text = re.sub(r'\{\{[^}]+\}\}', '', text)
    text = re.sub(r'\[\[([^]|]+\|)?([^]]+)\]\]', r'\2', text)
    text = re.sub(r"<sup>([^<]+)</sup>", r'\1', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'\'\'([^\']+)\'\'', r'\1', text)
    text = re.sub(r'! scope="row"\s*\|', '', text)
    
    # Handle ntsh/nts format
    text = re.sub(r'\{\{ntsh\|([^}]+)\}\}', r'\1', text)
    text = re.sub(r'\{\{nts\|([^}]+)\}\}', r'\1', text)
    
    text = text.strip()
    return text

def process_table(input_file, output_file):
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract table rows
    rows = re.findall(r'\|-[^|]*?\n(.*?)\n(?=\|-|\|})', content, re.DOTALL)
    total_rows = len(rows)
    
    # Prepare CSV data
    csv_data = []
    headers = ['Messier number', 'NGC/IC number', 'Common name', 'Image', 'Image small', 
              'Object type', 'Distance (kly)', 'Constellation', 'Apparent magnitude',
              'Apparent dimensions', 'Right ascension', 'Declination']

    for row_index, row in enumerate(rows, 1):
        print(f"Processing row {row_index} of {total_rows}...")
        
        # Split into columns and clean each cell
        cols = row.split('\n|')
        if len(cols) < 11:  # Skip invalid rows
            continue
            
        # Clean up the cells
        clean_cols = []
        for i, col in enumerate(cols):
            col = col.strip('| ')
            if col.startswith('style="'):
                col = col[col.find('|')+1:].strip()
            
            # Special handling for Distance column (index 6)
            if i == 5:  # Distance column
                clean_cols.append(clean_distance(col))
            else:
                clean_cols.append(clean_text(col))

        # Extract image filename
        image_match = re.search(r'\[\[File:(.*?)\|', row)
        if image_match:
            image_filename = image_match.group(1)
            commons_url = f"https://commons.wikimedia.org/wiki/File:{image_filename}"
            # Get full and thumbnail URLs
            full_url = get_wikimedia_url_via_api(commons_url)
            if full_url:
                # Download and convert images
                full_filename, small_filename = download_and_convert_image(full_url, row_index-1)
                full_url = full_filename
                small_url = small_filename
            else:
                full_url = ''
                small_url = ''
        else:
            full_url = ''
            small_url = ''

        # Create row data
        row_data = clean_cols[:3] + [full_url, small_url] + clean_cols[4:]
        csv_data.append(row_data)

    print("Writing data to CSV file...")
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(csv_data)
    
    print("Process completed!")

# Execute the conversion
process_table('table.txt', 'messier_objects.csv')