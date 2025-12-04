#!/usr/bin/env python3
"""
Test script to demonstrate flattening Trello card data to CSV
"""

from trello_export import export_cards_to_csv

if __name__ == "__main__":
    print("=" * 60)
    print("Trello Card Data Flattening and Export")
    print("=" * 60)
    print()
    
    # Export cards to CSV
    df = export_cards_to_csv("./out/trello_cards_export.csv")
    
    print("\n" + "=" * 60)
    print("Preview of exported data (first 5 rows):")
    print("=" * 60)
    print(df.head())
    
    print("\n" + "=" * 60)
    print("Column information:")
    print("=" * 60)
    print(df.info())
