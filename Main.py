"""
Main.py
-------
This is the terminal (command-line) version of the proposal generator.
No browser needed — just run it in the terminal and answer the questions.

WHY keep this?
  - Great for learning Python basics (input, functions, dictionaries).
  - Useful if you want to generate a proposal quickly without opening a browser.
  - Good for testing proposal_engine.py without Streamlit.

HOW TO RUN:
  python Main.py
"""

# ─────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────
# WHY import at the top?
#   Python needs to know what tools you're using before it runs your code.
#   Putting imports at the top is the standard convention — everyone does it.

import os
from proposal_engine import (
    Deliverables,
    create_proposal,
    save_as,
    save_pdf,
)


# ─────────────────────────────────────────────
# STEP 1 — Get information from the user
# ─────────────────────────────────────────────
# input() pauses the program and waits for the user to type something.
# Whatever they type is stored as a string in the variable.

print("\n" + "="*45)
print("       CLIENT PROPOSAL GENERATOR")
print("="*45 + "\n")

name         = input("Enter client name      : ").strip()
print("Project types: website | web application | mobile app | crm")
project_type = input("Enter project type     : ").strip().lower()
budget       = input("Enter budget (₹)       : ").strip()
timeline     = input("Enter timeline         : ").strip()


# ─────────────────────────────────────────────
# STEP 2 — Validate the project type
# ─────────────────────────────────────────────
# WHY validate?
#   If the user types "Website" instead of "website", the dictionary
#   lookup will fail.  We check early and give a helpful message.

if project_type not in Deliverables:
    print(f"\n⚠  '{project_type}' is not a recognised project type.")
    print(f"   Valid options: {', '.join(Deliverables.keys())}")
    exit(1)


# ─────────────────────────────────────────────
# STEP 3 — Build the client dictionary
# ─────────────────────────────────────────────
# WHY a dictionary?
#   Instead of passing 4 separate variables to every function,
#   we group them into one dictionary.  Clean and easy to extend.

client = {
    "Name":         name,
    "Project Type": project_type,
    "Budget":       budget,
    "Timeline":     timeline,
}


# ─────────────────────────────────────────────
# STEP 4 — Generate and display the proposal text
# ─────────────────────────────────────────────
proposal_text = create_proposal(client)
print(proposal_text)


# ─────────────────────────────────────────────
# STEP 5 — Save to files
# ─────────────────────────────────────────────
# WHY os.makedirs?
#   Creates the "proposals" folder if it doesn't exist yet.
#   exist_ok=True means it won't crash if the folder already exists.

os.makedirs("proposals", exist_ok=True)

# Save plain text version
txt_path = f"proposals/{client['Name']}_proposal.txt"
with open(txt_path, "w", encoding="utf-8") as file:
    file.write(proposal_text)
print(f"✅ Text file saved   : {txt_path}")

# Save Word document
docx_path = save_as(client, proposal_text)
print(f"✅ Word file saved   : {docx_path}")

# Save PDF
pdf_path = save_pdf(client)
print(f"✅ PDF file saved    : {pdf_path}")

print("\nDone! Check the 'proposals' folder.\n")
