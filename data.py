import os
import gspread

import requests
from datetime import datetime, date


class Saver:
    """
    Connects to Google Sheets API and saves data to the spreadsheet
    All connection parameters are stored in .env file
    Google Credentials are stored in google_credentials.json file
    """

    def __init__(self):
        self.service_account = gspread.service_account(filename="./google_credentials.json")

    def _get_spreadsheet(self, spreadsheet_name: str) -> gspread.Spreadsheet:
        """
        Will return spreadsheet object by name
        """
        return self.service_account.open(spreadsheet_name)

    def save_data(self, response: dict, from_place: str, to_place: str):
        """
        Will store response from the API
        """
        spreadsheet = self._get_spreadsheet(os.environ.get("SPREADSHEET_NAME"))
        worksheet = spreadsheet.worksheet(os.environ.get("WORKSHEET_NAME"))

        from_place_name = from_place[1]
        to_place_name = to_place[1]

        today = date.today().strftime("%d/%m/%Y")
        time = datetime.now().strftime("%H:%M:%S")
        distance = response["distance"]
        trip_time_sec = response["time"]
        trip_time_min = round(trip_time_sec / 60, 2)
        for trip in response["options"]:
            # car_class = trip.get("class_name")  # don't need it for now
            car_class_name = trip.get("class_text")
            price = trip.get("price")
            waiting_time = trip.get("waiting_time")
            # min_price = trip.get("min_price")  # don't need it for now
            worksheet.append_row(
                [
                    from_place_name,
                    to_place_name,
                    today,
                    time,
                    car_class_name,
                    price,
                    waiting_time,
                    trip_time_sec,
                    trip_time_min,
                    round(distance, 2),
                ],
            )


class Worker:
    """
    Sending requests to the Yandex API and return responses
    All connection parameters are stored in .env file
    """

    def __init__(self):
        self.car_classes = (os.environ.get("CAR_CLASSES"),)
        self.clid = os.environ.get("CLID")
        self.url = "https://taxi-routeinfo.taxi.yandex.net/taxi_info"
        self.headers = {
            "Content-Type": "application/json",
            "YaTaxi-Api-Key": os.environ.get("API_KEY"),
        }

    @staticmethod
    def _reverse_coords(coords: list) -> list:
        """
        Somehow, maps.yandex.ru returns coordinates in the wrong order
        This method will reverse them
        """
        stripped_coords = [ele.strip() for ele in coords]
        reversed_coords = ",".join([stripped_coords[-1], stripped_coords[0]])
        return reversed_coords

    def send_request(self, from_place: str, to_place: str) -> dict:
        """
        Will send request to the API
        """
        from_coords = self._reverse_coords(from_place[0].split(","))
        to_coords = self._reverse_coords(to_place[0].split(","))
        params = {
            "clid": self.clid,
            "rll": f"{from_coords}~{to_coords}",
            "class": self.car_classes,
        }
        return requests.get(self.url, headers=self.headers, params=params).json()
