import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.crud.company import company as CRUDCompany
from app.services.bigquery_writer import BigQueryWriter
from google.cloud import bigquery

# List of companies (name, vat)
COMPANIES = [
    {"name": "REAL MADRID CLUB DE FUTBOL", "vat": "G28034718"},
    {"name": "SOLVENTIS SV, S.A.", "vat": "a63593552"},
    {"name": "BANCO BILBAO VIZCAYA ARGENTARIA, S.A.", "vat": "A48265169"},
    {"name": "MUTUA MADRILEÑA AUTOMOVILISTA, S.S.P.F.", "vat": "V28027118"},
    {"name": "MERLIN PROPERTIES SOCIMI, S.A.", "vat": "A86977790"},
    {"name": "INFINORSA GESTION INMOBILIARIA Y FINANCIERA, S.A.", "vat": "A28342436"},
    {"name": "RAMONDIN,S.A.", "vat": "A20002648"},
    {"name": "TORRE DE ABRAHAM, S.L.", "vat": "B82860339"},
    {"name": "AMRESORTS MANAGEMENT SPAIN, S.L.U.", "vat": "B8731680"},
    {"name": "CIUDAD DEL MOTOR DE ARAGON, S.A.", "vat": "A44184216"},
    {"name": "REDEIA CORPORACION, S.A.", "vat": "A78003662"},
    {"name": "VOPI 4, S.A.", "vat": "A59345702"},
    {"name": "ERANOVUM E-MOBILITY, S.L.", "vat": "B05482310"},
    {"name": "ODILO TID, S.L.", "vat": "B30856439"},
    {"name": "PEKOS EUROPE GROUP, S.L.", "vat": "B66785643"},
    {"name": "Reganosa Holdco, S.A.", "vat": "A70537543"},
    {"name": "INSUD PHARMA, S.L.", "vat": "B85212165"},
    {"name": "DELOITTE ADVISORY, S.L.", "vat": "B86466448"},
    {"name": "NATURGY ENERGY GROUP, S.A.", "vat": "A08015497"},
    {"name": "CEREALTO GLOBAL, S.L.", "vat": "B47545132"},
    {"name": "OBRASCON HUARTE LAIN, S.A. (OHL)", "vat": "A48010573"},
    {"name": "EULEN SEGURIDAD, S.A.", "vat": "A28517308"},
    {"name": "AUTORIDAD PORTUARIA DE A CORUÑA", "vat": "Q1567003G"},
    {"name": "ENZICAS BIO, SL", "vat": "B10923191"},
    {"name": "CORPORACION ACCIONA INFRAESTRUCTURAS, S.L.", "vat": "B87324455"},
    {"name": "NADICO INDUSTRIAL MANAGEMENT, S.L.", "vat": "B63177109"},
    {"name": "KUTXABANK, S.A.", "vat": "A95653077"},
    {"name": "PricewaterhouseCoopers, S.L.", "vat": "B84980007"},
    {"name": "EIGO GESTION DE OBRAS, S.L.", "vat": "B99464281"},
    {"name": "EBRO FOODS, S.A.", "vat": "A47412333"},
    {"name": "SULAYR GLOBAL SERVICE,S.L.", "vat": "B18907196"},
]

BQ_TABLE = "solid-topic-443216-b2.risk_monitoring.companies"

def clear_bigquery_table(table_id: str):
    client = bigquery.Client()
    query = f"TRUNCATE TABLE `{table_id}`"
    client.query(query).result()
    print(f"Table {table_id} cleared.")

def main():
    db = SessionLocal()
    # Clear BigQuery table first
    clear_bigquery_table(BQ_TABLE)
    # Insert into SQLite as before
    for entry in COMPANIES:
        obj_in = {
            "vat": entry["vat"],
            "name": entry["name"],
        }
        for optional_field in [
            "description",
            "sector",
            "client_tier",
            "created_at",
            "updated_at",
        ]:
            if optional_field in entry:
                obj_in[optional_field] = entry[optional_field]
        existing = CRUDCompany.get_by_name(db, name=entry["name"])
        if not existing:
            CRUDCompany.create(db, obj_in=obj_in)
            print(f"Inserted: {entry['name']} ({entry['vat']})")
        else:
            print(f"Already exists: {entry['name']}")
    db.close()
    # Insert into BigQuery
    writer = BigQueryWriter(batch_size=50)
    for entry in COMPANIES:
        writer.queue(BQ_TABLE, entry)
    writer.flush()
    print("Companies inserted into BigQuery.")

if __name__ == "__main__":
    main()
