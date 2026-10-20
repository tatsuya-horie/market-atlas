#!/usr/bin/env python3
"""Optional derived fund NAV refresh from public downloadable CSVs.
If parsing or downloading fails, retain dated snapshots rather than guessing."""
import csv, io, json, re
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parents[1]
TARGET = BASE / "site/data/funds.json"
SOURCES = {
  "allcountry": "https://fs.bk.mufg.jp/webasp/mufg/fund/detail/chart/csv/m00355920.csv",
  "sp500fund": "https://fs.bk.mufg.jp/webasp/mufg/fund/detail/chart/csv/m00355320.csv",
}

def parsedate(v):
    v = str(v).strip().replace("年","/").replace("月","/").replace("日","")
    for fmt in ("%Y/%m/%d","%Y-%m-%d","%Y.%m.%d","%Y%m%d"):
        try:
            d = datetime.strptime(v, fmt).date()
            if date(2018,1,1) <= d <= datetime.now(ZoneInfo("Asia/Tokyo")).date():
                return d
        except ValueError: pass
    return None

def number(v):
    try:
        n = float(re.sub(r"[，,円\s　]", "", str(v)))
        if 100 < n < 10000000: return n
    except ValueError: pass
    return None

def load(url):
    request=Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"text/csv,*/*"})
    with urlopen(request, timeout=22) as response:
        raw=response.read(6000000)
    for codec in ("utf-8-sig","cp932","shift_jis","utf-16"):
        try: decoded=raw.decode(codec)
        except UnicodeError: continue
        sep="\t" if decoded.count("\t") > decoded.count(",")*2 else ","
        found={}
        for row in csv.reader(io.StringIO(decoded),delimiter=sep):
            if len(row)<2: continue
            d,n=parsedate(row[0]),number(row[1])
            if d and n is not None: found[d]=n
        if len(found)>=20:
            return [{"date":d.isoformat(),"value":found[d]} for d in sorted(found)]
    raise ValueError("Download not recognized as dated NAV history")

def summarise(hist, previous):
    latest=hist[-1]
    ld=date.fromisoformat(latest["date"])
    def before(d):
        return next((x for x in reversed(hist) if x["date"]<=d.isoformat()),None)
    monday=ld-timedelta(days=ld.weekday())
    lastfriday=monday-timedelta(days=3)
    monthend=ld.replace(day=1)-timedelta(days=1)
    try: lastyear=ld.replace(year=ld.year-1)
    except ValueError: lastyear=ld.replace(year=ld.year-1,day=28)
    baseline={
      "day":hist[-2], "week":before(lastfriday),
      "month":before(monthend), "year":before(lastyear),
    }
    changes={k: (round(100*(latest["value"]/v["value"]-1),4) if v else None) for k,v in baseline.items()}
    dates={k:(v["date"] if v else None) for k,v in baseline.items()}
    # Keep the last 390 days of actual NAV observations without weekly sampling.
    # At most ~270 trading days, appropriate for mobile SVG charts.
    cutoff=ld-timedelta(days=390)
    daily=[p for p in hist if date.fromisoformat(p["date"])>=cutoff]
    return {**previous,"latest":latest,"changes":changes,"comparison_dates":dates,"history":daily}

def main():
    obj=json.loads(TARGET.read_text(encoding="utf-8"))
    changed=0
    for key,url in SOURCES.items():
        try:
            history=load(url)
            old=obj["funds"][key]
            if history[-1]["date"]<old["latest"]["date"]:
                raise ValueError("Provider data older than existing verified snapshot")
            obj["funds"][key]=summarise(history,old)
            print(key,history[-1])
            changed+=1
        except Exception as error:
            print("No update",key,type(error).__name__,str(error))
    if changed:
        obj["generated_at"]=datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(timespec="seconds")
        obj["status"]="derived_official_csv_history"
        TARGET.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    else:
        print("All dates remain as previously labelled. No estimated prices inserted.")

if __name__=="__main__":
    main()
