import pandas as pd
from app.database import get_session
from app.models import Sale

def load_csv_to_db(csv_path: str):
    df = pd.read_csv(csv_path)
    session = get_session()

    for _, row in df.iterrows():
        sale = Sale(
            date=row["date"],
            week_day=row["week_day"],
            hour=row["hour"],
            ticket_number=row["ticket_number"],
            waiter=row["waiter"],
            product_name=row["product_name"],
            quantity=row["quantity"],
            unitary_price=row["unitary_price"],
            total=row["total"]
        )
        session.add(sale)

    session.commit()
