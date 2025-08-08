import re

def select_from_path(path, fancy=False, charts=False):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        source_data = f.read()

    vin = None
    m = re.search(r'<TD[^>]*CLASS="infotitle"[^>]*>\s*VIN\s*</TD>\s*<TD[^>]*CLASS="infovalue"[^>]*>\s*([^<]+)',
                  source_data, re.IGNORECASE)
    if m:
        vin = m.group(1).replace("(User)", "").strip()
    else:
        vals = re.findall(r'<TD[^>]*CLASS="infovalue"[^>]*>\s*([^<]+)', source_data, re.IGNORECASE)
        if len(vals) >= 5:
            vin = vals[4].replace("(User)", "").strip()
    vin = vin or "UNKNOWN_VIN"

    start = source_data.find('<TD CLASS="dataheader" WIDTH=50%>Raw Data 2</TD>')
    if start == -1:
        m2 = re.search(r'<TD[^>]*CLASS="dataheader"[^>]*>Raw\s*Data\s*2</TD>', source_data, re.IGNORECASE)
        start = m2.start() if m2 else -1
    if start != -1:
        end = source_data[start:].find("</TABLE>")
        seg = source_data[start+43:start+end] if end != -1 else source_data[start+43:]
        seg = re.sub(r"<.*?>", "", seg).replace("\n", "").replace(" ","")
        data = seg
    else:
        data = ""

    fMode = 1 if fancy else 0
    chartsOpt = 1 if charts else 0
    return vin, data, fMode, chartsOpt
