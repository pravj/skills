---
name: generate-weekly-update
description: Generate weekly update documents in .docx format following the established structure and formatting
user-invocable: true
---

# Weekly Update Generator

Generate weekly update documents in .docx format following the established structure and formatting.

## Inputs Required

When this skill is invoked, ask the user for:

1. **This week's helper document path** - The rough notes file (usually a .txt file with sections)
2. **Last week's final update document path** - The completed .docx file from previous week (used for POPW extraction, formatting template, and owner inference)
3. **Date range** - For the title (e.g., "9th February - 13th February week")

## Step 1: Generate Initial Draft

Use Python with python-docx library to create the draft document.

### 1.1 Setup and Template Loading

```python
from docx import Document
from docx.shared import Pt
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def add_bullet(paragraph, level=0, num_id=1):
    pPr = paragraph._element.get_or_add_pPr()
    numPr = parse_xml(r'<w:numPr %s><w:ilvl w:val="%d"/><w:numId w:val="%d"/></w:numPr>' % (nsdecls('w'), level, num_id))
    pPr.insert(0, numPr)

def set_font(paragraph, font_name='Arial', font_size=11):
    for run in paragraph.runs:
        run.font.name = font_name
        run.font.size = Pt(font_size)

# Load last week's .docx as template
doc = Document(last_week_path)

# Clear all paragraphs
for paragraph in doc.paragraphs[:]:
    p = paragraph._element
    p.getparent().remove(p)
```

### 1.2 Parse Helper Document

The helper document follows this structure pattern. Parse it flexibly:

**For each section**, content is provided as rough notes or semi-expanded text. Parse line by line:

- Section headers: "System / Process / Tools", "Good", "Bad", "Ugly", "Support Needed", "Pre-Sales / Sales-handover Stage", "Partners / Vendors", "Hiring / Onboarding", "Analytics / Reporting"
- Content lines: Everything after a section header until the next section header

**Special handling for System / Process / Tools**:
- Look for items starting with or containing "This week" - these go as main bullets with sub-bullets underneath
- Look for "Identified opportunities" or "Opportunity identified" - these signal the second part
- Items under "Identified opportunities" become sub-bullets under that item

**For Good/Bad/Ugly sections**:
- Each distinct topic becomes a **main bullet with title + owners**
- Details about that topic become **sub-bullets**
- Detect topic boundaries by:
  - Empty lines between topics
  - Or each line is a separate topic if no clear grouping

**Owner inference**:
- Try to match current topic with similar topic from last week's document
- If topic name contains similar keywords (e.g., "LaneHealth", "CBV", "Zolve"), copy owners from last week
- If no match or uncertain → use `[Owner Names]` placeholder

### 1.3 Document Generation

Generate sections in this exact order with proper formatting:

1. **Title**: "Update for [date_range]" (no bullets, normal font)
2. Blank line
3. **Summary**: Bold header, then placeholder "[TO BE GENERATED AFTER REVIEW]"
4. Two blank lines
5. **System / Process / Tools**:
   - Bold header
   - Blank line
   - Main bullet: "This week, [content]"
   - Sub-bullets for specific items
   - Main bullet: "Identified opportunities for upgrading the playbook in the following areas."
   - Sub-bullets for opportunities
   - Use num_id=1
6. Two blank lines
7. **Good**:
   - Bold header
   - Blank line
   - For each item:
     - Main bullet (level 0): "[Topic Title] - [Owners or [Owner Names]]"
     - Sub-bullets (level 1): Details about the item
   - Use num_id=2
8. Blank line
9. **Bad**: (same structure as Good, num_id=3)
10. Blank line
11. **Ugly**: (same structure as Good, num_id=4)
12. Blank line
13. **Support Needed**:
    - If single item: can be just main bullet
    - If multiple sub-points: main bullet title + sub-bullets
    - Use num_id=5
14. Blank line
15. **Pre-Sales / Sales-handover Stage**: Simple bullet list, num_id=6
16. Blank line
17. **Partners / Vendors**: Simple bullet list or title + details, num_id=7
18. Blank line
19. **Hiring / Onboarding**: Simple bullet list, num_id=8
20. Blank line
21. **Analytics / Reporting**: Each item usually has "- Name" at end, treat as separate bullets, num_id=9
22. Two blank lines
23. **Progress on the Previous Week's Bad / Ugly**: Placeholder "[TO BE COMPLETED]"

**Font**: Arial 11pt for ALL content
**Formatting**: Section headers bold, everything else normal weight

Save as `Update-[date-range]-DRAFT.docx`

## Step 2: Handle POPW (Progress on Previous Week's Bad/Ugly) Section

### 2.1 Extract Last Week's Items

Read last week's .docx and extract all items from "Bad" and "Ugly" sections:
- Each item has a title (level 0 bullet with owners)
- And details (level 1 bullets)

### 2.2 Comparison Logic

For each item from last week:

1. **Check if topic is already covered this week** by searching for keywords from last week's title in this week's Bad/Ugly sections
   - Example: "Pollack & Rosen Account Recall" from last week → look for "Pollack" or "P&R" or "Account Recall" in this week's items
   - If found → **SKIP this item** (don't add to POPW)

2. **If NOT covered** → Ask user for update

### 2.3 Interactive Questioning (ONE BY ONE)

For each uncovered item:
- Display: "**Item X of Y: [Title with Owners]**"
- Show last week's summary/details
- Ask: "What's the progress/update on this issue this week?"
- Wait for user response
- Move to next item

### 2.4 Context Enhancement for POPW

When user provides brief update (e.g., "solved", "still WIP", "now ahead by 3%"):

**Check if this week's document has relevant context to add**:
- If user says "solved" and System/Process/Tools mentions Team Lead playbook → add that context
- If user says "now ahead by 3%" and Good section has Zolve item → reference it
- Pattern: "[User's update]. [Context from this week's work if available]"

Example:
- User says: "This is now solved, we fixed the gaps"
- System/Process mentions: "We completed the Team Lead playbook" and "start-of-day huddles"
- POPW entry becomes:
  - Main: "Agent Break Time Management - Jugnu / Charles / Preetham"
  - Sub 1: "We've drafted the Team Lead playbook to provide clear operational guidance and accountability structures."
  - Sub 2: "We have started start-of-day and end-of-day huddles for Team Leads to keep a watch on break time adherence and address issues proactively."

**If user gives brief update with no context to pull** → use their exact words as-is

### 2.5 Update Document

Add all POPW items to the draft using:
- num_id=10
- Same structure: main bullet (title + owners) → sub-bullets (details)

## Step 3: Generate Summary (After User Review)

After user reviews and edits the draft document, ask if they're ready for summary generation.

**Read the edited draft** (not the helper document) to generate summary from actual content.

Generate following this exact structure:

```
This week, the focus was on [extract main theme from System/Process/Tools section - usually the "This week" bullet].

• In terms of small wins, [summarize 2-4 Good items with specific metrics/numbers - prioritize items with quantifiable results].

• As a loss, [summarize main Bad items - focus on client/revenue impact].

• We faced issues with [summarize operational/technical issues from Bad or Ugly that are issue-oriented].

• In terms of challenges, [summarize strategic/blocking challenges from Ugly section - focus on blockers].
```

**Writing style**:
- Professional, concise, executive-level
- Include specific numbers/metrics where available
- Focus on business impact
- Use past tense

Update the Summary section in the .docx file with this generated text (preserve bullet formatting).

## Important Notes

### Content Handling
- Helper document contains mix of rough notes and expanded content - **use as provided**
- Don't over-expand or add content not in helper
- User will polish after draft generation
- Preserve any numbers, metrics, or specific details from helper

### Owner Attribution
- Try to infer from last week's document by matching topic keywords
- If uncertain or no match → use `[Owner Names]` placeholder
- Never guess owners

### Parsing Flexibility
- Be flexible with section header variations (e.g., "System/Process/Tools" vs "System / Process / Tools")
- Handle both Windows and Unix line endings
- Skip empty lines appropriately

### Bullet Structure
- Must use Word's proper numbering XML (add_bullet function) so indent controls work
- Level 0 = main bullets (filled circles)
- Level 1 = sub-bullets (hollow circles)
- Different sections use different num_id values

### POPW Questioning
- ONE item at a time (Option B approach)
- Ask, wait for response, then next
- Don't batch questions

## Output

Final deliverable: `Update-[DateRange]-DRAFT.docx` ready for user to:
1. Fill in [Owner Names] placeholders
2. Expand any rough notes that need more detail
3. Add color coding to section headers if desired
4. Add hyperlinks if needed
5. Final review and send

