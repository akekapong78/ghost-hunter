from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List
import random
from sentence_transformers import SentenceTransformer
import psycopg2
import logging


# โหลด embedding model
embedder = SentenceTransformer("intfloat/multilingual-e5-small")

# Logging
logging.basicConfig(level=logging.INFO, format="%(message)s", encoding="utf-8")

# FastAPI app
app = FastAPI(title="Mock GIS Vector API")

# Request model
class NameRequest(BaseModel):
    name_string: str

# Response model
class GisVectorItem(BaseModel):
    ca_number: str
    pea_number: str
    customer_name: str
    customer_address: str
    office_code: str | None = None
    lat: float
    long: float
    billing_month: str | None = None
    similarity_score: float | None = None

class GisReportResponse(BaseModel):
    results: List[GisVectorItem]
    total: int
    success: bool
    message: str

# DB connection
def get_connection():
    return psycopg2.connect(
        dbname="vector_db",
        user="postgres",
        password="postgres",
        host="172.30.211.105",
        port="5432"
    )

@app.post("/gis-report", response_model=GisReportResponse)
def search(req: NameRequest = Body(...)):
    names = [n.strip() for n in req.name_string.split("|") if n.strip()]
    results: List[GisVectorItem] = []

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                for name in names:
                    # Option 1. Fuzzy matching using pg_trgm
                    cur.execute("SET pg_trgm.similarity_threshold = 0.5;")
                    cur.execute("""
                        SELECT 
                            ca_number, 
                            pea_number, 
                            LEFT(customer_name, LENGTH(customer_name) - 5) || REPEAT('*', 5) AS customer_name,
                            customer_address, 
                            office_code, 
                            lat, 
                            long, 
                            billing_month,
                            similarity(customer_name, %s) AS similarity_score                            
                        FROM gis_vector
                        WHERE customer_name %% %s
                        ORDER BY similarity_score DESC
                        LIMIT 1;
                    """, (name, name))
                    rows = cur.fetchall()
                    for row in rows:
                        results.append(GisVectorItem(
                            ca_number=row[0],
                            pea_number=row[1],
                            customer_name=row[2],
                            customer_address=row[3],
                            office_code=row[4],
                            lat=float(row[5]),
                            long=float(row[6]),
                            billing_month=row[7],
                            similarity_score=float(row[8]),
                        ))
                    if len(rows) > 0:
                        logging.info(f"done fuzzy: {name}")
                        continue

                    # Obtion 2. embedding similarity
                    query_embedding = embedder.encode(name).tolist()
                    cur.execute("""
                        SELECT 
                            ca_number, 
                            pea_number, 
                            LEFT(customer_name, LENGTH(customer_name) - 5) || REPEAT('*', 5) AS customer_name,
                            customer_address, 
                            office_code, 
                            lat, 
                            long, 
                            billing_month,
                            1 - (embedding <=> %s::vector) AS similarity_score
                        FROM gis_vector
                        WHERE embedding IS NOT NULL
                        ORDER BY embedding <=> %s::vector
                        LIMIT 1;
                    """, (query_embedding, query_embedding))
                    rows = cur.fetchall()
                    for row in rows:
                        results.append(GisVectorItem(
                            ca_number=row[0],
                            pea_number=row[1],
                            customer_name=row[2],
                            customer_address=row[3],
                            office_code=row[4],
                            lat=float(row[5]),
                            long=float(row[6]),
                            billing_month=row[7],
                            similarity_score=float(row[8]),
                        ))
                    logging.info(f"done embedding: {name}")

    except Exception as e:
        logging.error(e)
        return GisReportResponse(results=[], total=0, success=False, message=str(e))

    return GisReportResponse(results=results, total=len(results), success=True, message="success")


# mock function
def mock_row(name: str) -> GisVectorItem:
    return GisVectorItem(
        ca_number=str(random.randint(1000000000, 9999999999)),
        pea_number=str(random.randint(10000000, 99999999)),
        customer_name=name,
        customer_address=f"ที่อยู่ของ {name}",
        office_code=f"L000{random.randint(1, 10)}",
        lat=round(random.uniform(6.5, 18.5), 6),
        long=round(random.uniform(98.0, 105.0), 6),
        billing_month=f"2025{random.randint(1, 12)}",
        similarity_score=None
    )

@app.post("/gis-report-mock", response_model=List[GisVectorItem])
def mock_search(req: NameRequest = Body(...)):
    names = [n.strip() for n in req.name_string.split("|") if n.strip()]
    return [mock_row(name) for name in names]


@app.get("/health")
def health_check():
    return {"status": "ok", "version": 2.0, "message": "update indexing for faster"}

# uv run uvicorn server:app --reload
# cd nssm-2.24\win64
# nssm start ghost-hunter-api