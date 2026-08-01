"""
exporter.py - Export SGTPA records to Excel/CSV.
"""
from datetime import datetime
import pandas as pd
from openpyxl.styles import Font

COLUMNS=[
"Company Name","Contact Person","Phone","Mobile","Email",
"Website","Address","Description","Category","Profile URL","Scraped At"
]

class Exporter:
    def __init__(self,records):
        self.records=records

    def dataframe(self):
        rows=[]
        for r in self.records:
            row={c:r.get(c,"") for c in COLUMNS if c!="Scraped At"}
            row["Scraped At"]=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            rows.append(row)
        df=pd.DataFrame(rows,columns=COLUMNS)
        df.drop_duplicates(subset=["Profile URL"],inplace=True)
        df.sort_values("Company Name",inplace=True,ignore_index=True)
        return df

    def to_excel(self,filename="SGTPA_Members.xlsx"):
        df=self.dataframe()
        with pd.ExcelWriter(filename,engine="openpyxl") as writer:
            df.to_excel(writer,index=False,sheet_name="Members")
            ws=writer.sheets["Members"]
            for cell in ws[1]:
                cell.font=Font(bold=True)
            for col in ws.columns:
                length=max(len(str(c.value or "")) for c in col)
                ws.column_dimensions[col[0].column_letter].width=min(max(length+2,15),60)
        return filename

    def to_csv(self,filename="SGTPA_Members.csv"):
        self.dataframe().to_csv(filename,index=False,encoding="utf-8-sig")
        return filename

if __name__=="__main__":
    sample=[{"Company Name":"Demo","Profile URL":"https://example.com"}]
    e=Exporter(sample)
    print(e.to_excel())
    print(e.to_csv())
