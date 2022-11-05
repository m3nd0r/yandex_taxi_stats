import csv
import logging

from data import Saver, Worker
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    filename="log_file.log",
    level=logging.ERROR,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


worker = Worker()
saver = Saver()

with open("input_data/from_input.csv", encoding="utf-8") as from_input_csv_file:
    from_input_reader = csv.reader(from_input_csv_file, delimiter=";")
    next(from_input_csv_file)  # for now - just skip the header
    for from_row in from_input_reader:
        with open("input_data/to_input.csv", encoding="utf-8") as to_input_csv_file:
            to_input_reader = csv.reader(to_input_csv_file, delimiter=";")
            next(to_input_csv_file)  # for now - just skip the header
            for to_row in to_input_reader:
                try:
                    response = worker.send_request(from_row, to_row)
                    saver.save_data(response, from_row, to_row)
                except Exception as e:
                    logger.error(f"Error: {e}", exc_info=True)
