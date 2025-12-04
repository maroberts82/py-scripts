# Trello Export Tool

This tool processes Trello export data and provides various export formats for analysis.

## Features

### 1. Card Data Flattening (NEW!)

The tool can now read Trello card data and flatten it into a CSV format that's easy to import into spreadsheets like Excel, Google Sheets, etc.

**Usage:**

```python
from trello_export import export_cards_to_csv

# Export all cards to CSV
df = export_cards_to_csv("./out/trello_cards_export.csv")
```

Or run the test script:

```bash
python3 test_export.py
```

**Exported Columns:**

- **ID**: Trello card ID
- **Card Name**: Full card title
- **Card Type**: Extracted from card name (e.g., "essential", "enhancement", "issue")
- **Points**: Story points extracted from card name
- **Description**: Card description
- **List**: The list/lane the card belongs to
- **Labels**: Comma-separated list of labels
- **Members**: Comma-separated list of assigned members
- **Due Date**: Card due date (if set)
- **Closed**: Whether the card is closed
- **Date Last Activity**: Last activity timestamp
- **URL**: Direct link to the card
- **Short Link**: Short Trello link
- **Checklist Count**: Number of checklists on the card
- **Attachment Count**: Number of attachments

### 2. Sprint Summary Report

The original functionality generates a detailed sprint summary report.

**Usage:**

Edit the `main()` function to specify which lanes to process, then run:

```bash
python3 trello_export.py
```

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Place your Trello export JSON file in the `data/` directory

3. Update the file path in `get_card_data()` function if needed

## Data Source

The tool expects a Trello board export in JSON format. To export your board:

1. Open your Trello board
2. Click "Show Menu" → "More" → "Print and Export"
3. Select "Export as JSON"
4. Save the file to the `data/` directory

## Output

- CSV files are saved to `./out/` directory
- Text summaries are saved to `./out/` directory as specified

## Requirements

- Python 3.7+
- pandas >= 2.0.0
- See `requirements.txt` for full list
