import json
import re
import pandas as pd
import sys
from datetime import datetime


def get_card_data():
    f = open('./data/sb-tto-15- software-trello-tickets.json')
    # f = open('./data/trello_card_data.json')
    # f = open('./data/zzzz.json')
    data = json.load(f)

    # for i in data['emp_details']:
    #     print(i)
    
    f.close()

    return data


def get_list_id(card_title, card_data):
    item_id = None

    list_data = card_data["lists"]
    for item in list_data:
        if item["name"] == card_title:            
            item_id  = item["id"]
            break

    return item_id

def get_cards_in_list(list_id, card_data):
    cards = []

    card_list_data = card_data["cards"]
    for card in card_list_data:
        if card["idList"] == list_id and card["closed"] == False:            
            cards.append(card)

    return cards

def get_card_names(list_of_cards):
    return_card_data = []

    for card in list_of_cards: 
        return_card_data.append(card["name"])

    return return_card_data    


def write_names_to_file(output_file, card_names):
    file = open(output_file, 'w')
    for name in card_names:
        clean_name = re.sub('\[.*\]', '', name).strip()
        file.write(clean_name+"\n")
    file.close()


def parse_card_name(card_name):
    """
    Extracts type and points from a Trello card name like:
    [essential - 3] Schema Creation: ...
    Returns (type, points) where points is int or None if 'P'.
    """
    match = re.match(r'\[(.*?)\s*-\s*(\d+|P)\]', card_name)
    if match:
        card_type = match.group(1).strip().lower()
        points_raw = match.group(2)
        points = None if points_raw == 'P' else int(points_raw)
        return card_type, points
    return None, None


def flatten_card_data_to_dataframe(card_data):
    """
    Flatten Trello card data into a pandas DataFrame suitable for spreadsheet import.
    
    Args:
        card_data: Dictionary containing Trello export data
        
    Returns:
        pandas DataFrame with flattened card information
    """
    cards = card_data.get("cards", [])
    lists = card_data.get("lists", [])
    labels = card_data.get("labels", [])
    members = card_data.get("members", [])
    
    # Create lookup dictionaries for easy reference
    list_lookup = {lst["id"]: lst["name"] for lst in lists}
    label_lookup = {lbl["id"]: lbl["name"] for lbl in labels}
    member_lookup = {mem["id"]: mem["fullName"] for mem in members}
    
    # Flatten card data
    flattened_cards = []
    
    for card in cards:
        # Parse card name for type and points
        card_type, points = parse_card_name(card.get("name", ""))
        
        # Extract label names
        card_labels = [label_lookup.get(lbl_id, lbl_id) for lbl_id in card.get("idLabels", [])]
        
        # Extract member names
        card_members = [member_lookup.get(mem_id, mem_id) for mem_id in card.get("idMembers", [])]
        
        # Parse dates
        date_last_activity = card.get("dateLastActivity", "")
        date_created = card.get("dateCompleted", "")
        due_date = card.get("due", "")
        
        flattened_card = {
            "ID": card.get("id", ""),
            "Card Name": card.get("name", ""),
            "Card Type": card_type if card_type else "",
            "Points": points if points is not None else "",
            "Description": card.get("desc", ""),
            "List": list_lookup.get(card.get("idList", ""), ""),
            "Labels": ", ".join(card_labels) if card_labels else "",
            "Members": ", ".join(card_members) if card_members else "",
            "Due Date": due_date,
            "Closed": card.get("closed", False),
            "Date Last Activity": date_last_activity,
            "URL": card.get("url", ""),
            "Short Link": card.get("shortLink", ""),
            "Checklist Count": len(card.get("idChecklists", [])),
            "Attachment Count": len(card.get("attachments", [])),
        }
        
        flattened_cards.append(flattened_card)
    
    # Create DataFrame
    df = pd.DataFrame(flattened_cards)
    
    return df


def export_cards_to_csv(output_csv="./out/trello_cards_export.csv"):
    """
    Read Trello card data and export to CSV for easy spreadsheet import.
    
    Args:
        output_csv: Path to output CSV file
    """
    print("Reading Trello card data...")
    card_data = get_card_data()
    
    print("Flattening card data...")
    df = flatten_card_data_to_dataframe(card_data)
    
    # Sort by list and card name
    df = df.sort_values(by=["List", "Card Name"])
    
    print(f"Exporting {len(df)} cards to {output_csv}...")
    df.to_csv(output_csv, index=False)
    
    print(f"\nExport complete!")
    print(f"Total cards exported: {len(df)}")
    print(f"Columns: {', '.join(df.columns)}")
    print(f"\nSummary by List:")
    print(df["List"].value_counts())
    
    return df


def main():
    print("hey there, processing your trello data...")    
    
    # List of Trello lane names to process
    trello_lane_names = [
        "Final Sprint - Completed",
        "Sprint #15 - Closed",
        # "Sprint #12 - Closed"
    ]
    print(f"getting cards from lanes: {', '.join(trello_lane_names)}")
    
    num_of_research_meeting_cards = 7
    num_of_research_meeting_points = 7
    
    output_file = "./out/sprint_15.txt"
    print(f"writing card names to: {output_file}")

    card_data = get_card_data()
    
    # Collect all cards from all specified lanes
    all_card_titles = []
    for lane_name in trello_lane_names:
        list_id = get_list_id(lane_name, card_data)
        if list_id:
            list_of_cards = get_cards_in_list(list_id, card_data)
            lane_card_titles = get_card_names(list_of_cards)
            all_card_titles.extend(lane_card_titles)
            print(f"  Found {len(lane_card_titles)} cards in '{lane_name}'")
        else:
            print(f"  Warning: Lane '{lane_name}' not found")
    
    card_titles = all_card_titles

    # Group card names by type and calculate totals
    summary = {}
    grouped_names = {}
    grouped_by_app = {}
    total_cards = 0
    total_points = 0
    for name in card_titles:
        card_type, points = parse_card_name(name)
        # If brackets are missing, assign default point and General section
        has_brackets = bool(re.search(r'\[.*?\]', name))
        if card_type:
            if card_type not in summary:
                summary[card_type] = {'count': 0, 'points': 0}
                grouped_names[card_type] = []
                grouped_by_app[card_type] = {}
            summary[card_type]['count'] += 1
            grouped_names[card_type].append(name)
            # Split into app section and title
            parts = name.split(':', 1)
            if len(parts) == 2:
                app_section_raw = parts[0].strip()
                app_section = re.sub(r'\[.*?\]', '', app_section_raw).strip()
                title = parts[1].strip()
                has_app_brackets = bool(re.search(r'\[.*?\]', app_section_raw))
            else:
                app_section = 'General'
                title = re.sub(r'\[.*?\]', '', name).strip()
                has_app_brackets = False
            # If brackets missing in card name or app section, assign default point and General section
            if not has_brackets or not has_app_brackets:
                if points is None:
                    points = 1
                app_section = 'General'
            if app_section not in grouped_by_app[card_type]:
                grouped_by_app[card_type][app_section] = []
            grouped_by_app[card_type][app_section].append(title)
            if points is not None:
                summary[card_type]['points'] += points
                total_points += points
            total_cards += 1

    # Write output to file
    with open(output_file, 'w') as f:
        f.write(f"Trello Card Summary\n")
        f.write(f"Processed Lanes: {', '.join(trello_lane_names)}\n\n")
        f.write(f"Total points: {total_points}\n")
        f.write(f"Total cards: {total_cards}\n\n")
        f.write(f"Including Research Meeting Cards:\n")
        total_cards_with_research = total_cards + num_of_research_meeting_cards
        total_points_with_research = total_points + num_of_research_meeting_points
        f.write(f"Total points (with research meetings): {total_points_with_research}\n")
        f.write(f"Total cards (with research meetings): {total_cards_with_research}\n\n")
        f.write("By card type:\n")
        for card_type, stats in summary.items():
            f.write(f"- {card_type.title()}: {stats['count']} cards, {stats['points']} points\n")
        f.write("\nGrouped Card Names by Type and Application Section:\n")
        card_type_order = ["customer request", "issue", "essential", "enhancement", "general"]
        for card_type in card_type_order:
            if card_type in grouped_by_app:
                f.write(f"\n{card_type.title()}\n")
                for app_section, titles in grouped_by_app[card_type].items():
                    clean_app_section = re.sub(r'\[.*?\]', '', app_section).strip()
                    f.write(f"  {clean_app_section}\n")
                    for title in titles:
                        f.write(f"    - {title}\n")
        # Write any remaining card types not in the order
        for card_type in grouped_by_app:
            if card_type not in card_type_order:
                f.write(f"\n{card_type.title()}\n")
                for app_section, titles in grouped_by_app[card_type].items():
                    clean_app_section = re.sub(r'\[.*?\]', '', app_section).strip()
                    f.write(f"  {clean_app_section}\n")
                    for title in titles:
                        f.write(f"    - {title}\n")

    # Print summary to console as well
    print("\nTrello Card Summary:")
    print(f"Processed Lanes: {', '.join(trello_lane_names)}")
    print(f"Total cards: {total_cards}")
    print(f"Total points: {total_points}")
    print(f"\nIncluding Research Meeting Cards:")
    total_cards_with_research = total_cards + num_of_research_meeting_cards
    total_points_with_research = total_points + num_of_research_meeting_points
    print(f"Total cards (with research meetings): {total_cards_with_research}")
    print(f"Total points (with research meetings): {total_points_with_research}")
    print("\nBy card type:")
    for card_type, stats in summary.items():
        print(f"- {card_type.title()}: {stats['count']} cards, {stats['points']} points")
    print("\nGrouped Card Names by Type and Application Section:")
    card_type_order = ["customer request", "issue", "essential", "enhancement", "general"]
    for card_type in card_type_order:
        if card_type in grouped_by_app:
            print(f"\n{card_type.title()}:")
            for app_section, titles in grouped_by_app[card_type].items():
                clean_app_section = re.sub(r'\[.*?\]', '', app_section).strip()
                print(f"  {clean_app_section}:")
                for title in titles:
                    print(f"    - {title}")
    # Print any remaining card types not in the order
    for card_type in grouped_by_app:
        if card_type not in card_type_order:
            print(f"\n{card_type.title()}:")
            for app_section, titles in grouped_by_app[card_type].items():
                clean_app_section = re.sub(r'\[.*?\]', '', app_section).strip()
                print(f"  {clean_app_section}:")
                for title in titles:
                    print(f"    - {title}")

    print("\nThat was fun, goodbye.")
  
  
# __name__
if __name__=="__main__":
    # Check command-line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command in ['csv', 'export']:
            # Export cards to CSV
            output_file = sys.argv[2] if len(sys.argv) > 2 else "./out/trello_cards_export.csv"
            export_cards_to_csv(output_file)
        elif command in ['summary', 'sprint']:
            # Run the original sprint summary logic
            main()
        elif command in ['help', '-h', '--help']:
            print("Usage:")
            print("  python trello_export.py [command] [options]")
            print()
            print("Commands:")
            print("  csv, export [output_file]  - Export cards to CSV (default: ./out/trello_cards_export.csv)")
            print("  summary, sprint            - Generate sprint summary report (original logic)")
            print("  help, -h, --help           - Show this help message")
            print()
            print("Examples:")
            print("  python trello_export.py csv")
            print("  python trello_export.py csv ./out/my_cards.csv")
            print("  python trello_export.py summary")
        else:
            print(f"Unknown command: {command}")
            print("Run 'python trello_export.py help' for usage information")
    else:
        # Default: run the original sprint summary logic
        print("Running default sprint summary...")
        print("Tip: Run 'python trello_export.py help' to see all available commands")
        print()
        main()