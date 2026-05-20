import requests
import time
import json
import csv
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

URL = "https://fxapi.app/api/usd/eur.json"
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "test_eur_usd.csv"


@dataclass
class ResponseRecord:
	status: int
	timestamp: str
	response: Optional[Any]

	def formatted(self) -> str:
		resp = self.response
		if isinstance(resp, (dict, list)):
			resp_str = json.dumps(resp, ensure_ascii=False)
		else:
			resp_str = str(resp)
		return f"[{self.timestamp}] status={self.status} response={resp_str}"


def print_record(rec: ResponseRecord) -> None:
	print(rec.formatted())

	# append record to CSV
	try:
		with open(CSV_PATH, "a", newline="", encoding="utf-8") as fh:
			writer = csv.writer(fh)
			writer.writerow([
				rec.timestamp,
				rec.status,
				json.dumps(rec.response, ensure_ascii=False),
			])
	except Exception as e:
		print(f"Failed to write CSV: {e}")


def init_csv(path: Path) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	with open(path, "w", newline="", encoding="utf-8") as fh:
		writer = csv.writer(fh)
		writer.writerow(["timestamp", "status", "response"])


def fetch_fxapi_data(url: str, iterations: int = 5, delay_sec: float = 1.0) -> None:
	for i in range(iterations):
		resp = requests.get(url)
		# try parse JSON, fall back to text
		parsed: Any
		try:
			parsed = resp.json()
		except ValueError:
			parsed = resp.text

		rec = ResponseRecord(
			status=resp.status_code,
			timestamp=datetime.utcnow().isoformat() + "Z",
			response=parsed,
		)
		print_record(rec)
		if i < iterations - 1:
			time.sleep(delay_sec)


if __name__ == "__main__":
	N = 20
	DELAY = 1.0
	init_csv(CSV_PATH)
	fetch_fxapi_data(URL, iterations=N, delay_sec=DELAY)

 