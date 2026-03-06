"""Convert project-summary.md to a styled HTML file, then open for PDF print."""
import markdown
from pathlib import Path

md_path = Path(__file__).parent / "project-summary.md"
html_path = Path(__file__).parent / "project-summary.html"

md_text = md_path.read_text(encoding="utf-8")

# Convert markdown to HTML
html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

# Wrap in full HTML with print-ready styling
html_full = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>ASAG Perturbation Framework — Project Summary</title>
<style>
  @page {{
    size: A4;
    margin: 2.5cm 2cm;
  }}
  @media print {{
    body {{ font-size: 10pt; }}
    h1 {{ font-size: 18pt; }}
    h2 {{ page-break-before: auto; }}
  }}
  body {{
    font-family: -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.65;
    color: #1a1a1a;
    max-width: 800px;
    margin: 0 auto;
    padding: 40px 24px;
  }}
  h1 {{
    font-size: 22pt;
    color: #1a3a5c;
    border-bottom: 2.5px solid #1a3a5c;
    padding-bottom: 10px;
    margin-top: 0;
  }}
  h2 {{
    font-size: 16pt;
    color: #2c5f8a;
    margin-top: 32px;
    border-bottom: 1px solid #ddd;
    padding-bottom: 5px;
  }}
  h3 {{
    font-size: 12.5pt;
    color: #3a7ab5;
    margin-top: 22px;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 14px 0;
    font-size: 10pt;
  }}
  th {{
    background-color: #2c5f8a;
    color: white;
    padding: 8px 12px;
    text-align: left;
    font-weight: 600;
  }}
  td {{
    padding: 7px 12px;
    border-bottom: 1px solid #e0e0e0;
  }}
  tr:nth-child(even) td {{
    background-color: #f8f9fa;
  }}
  code {{
    background-color: #f0f2f5;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 9.5pt;
    font-family: 'SF Mono', Menlo, Consolas, monospace;
  }}
  pre {{
    background-color: #f0f2f5;
    padding: 14px 18px;
    border-radius: 6px;
    font-size: 9pt;
    line-height: 1.45;
    overflow-x: auto;
  }}
  pre code {{
    background: none;
    padding: 0;
  }}
  blockquote {{
    border-left: 3.5px solid #2c5f8a;
    margin: 12px 0;
    margin-left: 0;
    padding: 10px 18px;
    background-color: #f5f7fa;
    color: #3a3a3a;
    font-style: italic;
  }}
  hr {{
    border: none;
    border-top: 1px solid #ddd;
    margin: 28px 0;
  }}
  p {{ margin: 10px 0; }}
  li {{ margin: 5px 0; }}
  ul, ol {{ padding-left: 24px; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

html_path.write_text(html_full, encoding="utf-8")
print(f"HTML written to: {html_path}")
print(f"Open in browser and use Cmd+P (Print > Save as PDF) to generate PDF.")
