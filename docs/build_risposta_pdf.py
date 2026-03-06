"""Convert risposta-professore.md to styled HTML for PDF export."""
import markdown
from pathlib import Path

md_path = Path(__file__).parent / "risposta-professore.md"
html_path = Path(__file__).parent / "risposta-professore.html"

md_text = md_path.read_text(encoding="utf-8")
html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

html_full = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<title>Proposta Metodologica — ASAG Perturbation Framework</title>
<style>
  @page {{
    size: A4;
    margin: 2.5cm 2cm;
  }}
  @media print {{
    body {{ font-size: 10.5pt; }}
    h1 {{ font-size: 18pt; page-break-before: avoid; }}
    h2 {{ page-break-before: auto; }}
    table {{ page-break-inside: avoid; }}
  }}
  body {{
    font-family: 'Georgia', 'Times New Roman', serif;
    font-size: 11.5pt;
    line-height: 1.7;
    color: #1a1a1a;
    max-width: 780px;
    margin: 0 auto;
    padding: 40px 28px;
  }}
  h1 {{
    font-family: -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 22pt;
    color: #1a1a1a;
    border-bottom: 2px solid #333;
    padding-bottom: 10px;
    margin-top: 0;
    margin-bottom: 4px;
  }}
  h1 + p {{
    margin-top: 4px;
    color: #555;
    font-style: italic;
  }}
  h2 {{
    font-family: -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 15pt;
    color: #1a3a5c;
    margin-top: 34px;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4px;
  }}
  h3 {{
    font-family: -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 12pt;
    color: #2c5f8a;
    margin-top: 22px;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    margin: 14px 0;
    font-size: 10pt;
    font-family: -apple-system, 'Helvetica Neue', Helvetica, Arial, sans-serif;
  }}
  th {{
    background-color: #1a3a5c;
    color: white;
    padding: 8px 12px;
    text-align: left;
    font-weight: 600;
  }}
  td {{
    padding: 7px 12px;
    border-bottom: 1px solid #ddd;
  }}
  tr:nth-child(even) td {{
    background-color: #f5f7fa;
  }}
  strong {{
    color: #1a1a1a;
  }}
  em {{
    color: #444;
  }}
  hr {{
    border: none;
    border-top: 1px solid #ccc;
    margin: 30px 0;
  }}
  p {{ margin: 10px 0; text-align: justify; }}
  li {{ margin: 5px 0; }}
  ul, ol {{ padding-left: 26px; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

html_path.write_text(html_full, encoding="utf-8")
print(f"HTML written to: {html_path}")
print(f"Open in browser and use Cmd+P > Save as PDF")
