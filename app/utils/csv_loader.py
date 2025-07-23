import csv
import logging
from typing import Iterator, List, Dict, Any
from sqlalchemy import text
from app.database import get_session
from app.models import Sale

logger = logging.getLogger(__name__)

def load_csv_streaming(csv_path: str, batch_size: int = 1000):
    """
    Loads CSV using streaming by chunks for scalability.
    Does not load the entire file into memory at once.
    """
    logger.info(f"Starting streaming load of {csv_path} with batch_size={batch_size}")
    
    total_records = 0
    session = get_session()
    
    try:
        # Process file in chunks without loading everything into memory
        for batch in _read_csv_chunks(csv_path, batch_size):
            _bulk_insert_batch(session, batch)
            total_records += len(batch)
            logger.info(f"Processed {total_records} records...")
        
        session.commit()
        logger.info(f"Load completed: {total_records} records processed")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error during load: {e}")
        raise
    finally:
        session.close()

def _read_csv_chunks(csv_path: str, batch_size: int) -> Iterator[List[Dict[str, Any]]]:
    """
    Reads CSV in chunks without loading the entire file into memory.
    Generates batches of records for efficient processing.
    """
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        batch = []
        
        for row in reader:
            # Process and validate each row
            processed_row = {
                'date': row['date'],
                'week_day': row['week_day'], 
                'hour': row['hour'],
                'ticket_number': row['ticket_number'],
                'waiter': int(row['waiter']),
                'product_name': row['product_name'],
                'quantity': float(row['quantity']),
                'unitary_price': float(row['unitary_price']),
                'total': float(row['total'])
            }
            batch.append(processed_row)
            
            # Send batch when it reaches desired size
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        # Send final batch if it has records
        if batch:
            yield batch

def _bulk_insert_batch(session, batch: List[Dict[str, Any]]):
    """
    Inserts batch using bulk operations for maximum efficiency.
    Much faster than inserting one by one.
    """
    # Use bulk insert for maximum performance
    session.execute(
        text("""
            INSERT INTO sales (date, week_day, hour, ticket_number, waiter, 
                             product_name, quantity, unitary_price, total)
            VALUES (:date, :week_day, :hour, :ticket_number, :waiter,
                   :product_name, :quantity, :unitary_price, :total)
        """),
        batch
    )

def load_csv_to_db(csv_path: str):
    """
    Main loading function with existing data verification.
    Uses streaming by default for scalability.
    """
    session = get_session()
    try:
        # Check if data already exists
        existing_count = session.query(Sale).count()
        logger.info(f"Existing records in DB: {existing_count}")
        
        if existing_count == 0:
            # Only load if no data exists
            load_csv_streaming(csv_path)
        else:
            logger.info("Data already exists, skipping load")
            
    finally:
        session.close()
