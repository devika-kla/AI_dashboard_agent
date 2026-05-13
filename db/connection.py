from sqlalchemy import create_engine, text
import pandas as pd

from config import settings


engine = create_engine(f"sqlite:///{settings.DB_PATH}")


SCHEMA = """
Album(AlbumId, Title, ArtistId)
Artist(ArtistId, Name)
Customer(CustomerId, FirstName, LastName, Country)
Employee(EmployeeId, FirstName, LastName, Title)
Genre(GenreId, Name)
Invoice(InvoiceId, CustomerId, InvoiceDate, BillingCountry, Total)
InvoiceLine(InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity)
MediaType(MediaTypeId, Name)
Playlist(PlaylistId, Name)
PlaylistTrack(PlaylistId, TrackId)
Track(TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, UnitPrice)
"""

def execute_sql(sql: str) -> pd.DataFrame:
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        rows = result.fetchall()
        columns = result.keys()

    return pd.DataFrame(rows, columns=columns)