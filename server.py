from fastapi import FastAPI, Body
from pydantic import BaseModel
from typing import List
import random
from sentence_transformers import SentenceTransformer
import psycopg2

# โหลด embedding model
embedder = SentenceTransformer("intfloat/multilingual-e5-small")

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

# DB connection
def get_connection():
    return psycopg2.connect(
        dbname="rag-pea",
        user="leocan",
        password="leocanza",
        host="localhost",
        port="5432"
    )

@app.post("/gis-report", response_model=List[GisVectorItem])
def search(req: NameRequest = Body(...)):
    names = [n.strip() for n in req.name_string.split("|") if n.strip()]
    results: List[GisVectorItem] = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            for name in names:
                query_embedding = embedder.encode(name).tolist()
                cur.execute("""
                    SELECT ca_number, pea_number, customer_name, customer_address, lat, long,
                           1 - (embedding <=> %s::vector) AS similarity_score
                    FROM gis_vector
                    ORDER BY similarity_score DESC
                    LIMIT 5;
                """, (query_embedding,))
                rows = cur.fetchall()

                for row in rows:
                    results.append(GisVectorItem(
                        ca_number=row[0],
                        pea_number=row[1],
                        customer_name=row[2],
                        customer_address=row[3],
                        office_code=None,
                        lat=float(row[4]),
                        long=float(row[5]),
                        billing_month=None,
                        similarity_score=float(row[6]),
                    ))
    return results


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