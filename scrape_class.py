from typing import List
import pandas as pd
from pandas.core.frame import collections
from pandas.io.api import ExcelWriter
import requests

from bs4 import BeautifulSoup


def parse_date(jadwal_str: str, hari_dict: dict, kelas: str, lokasi: str):
    jam_list = jadwal_str.split("/")
    if len(jam_list) > 0:
        for jam in jam_list:
            jam = int(jam) if jam != "" else jam
            if jam not in hari_dict:
                hari_dict[jam] = {}

            hari_dict[jam][kelas] = lokasi


def scrape_schedule(kelas: str):
    senin = {}
    selasa = {}
    rabu = {}
    kamis = {}
    jumat = {}
    sabtu = {}

    for nomor_kelas in range(1, 1000):
        if nomor_kelas < 10:
            url = f"http://baak.gunadarma.ac.id/jadwal/cariJadKul?_token=uWi5TB481or7ej8uz7hczKyDtOR4xSbRDxJp7QxK&teks={kelas}0{nomor_kelas}&filter=*.html"
        else:
            url = f"http://baak.gunadarma.ac.id/jadwal/cariJadKul?_token=uWi5TB481or7ej8uz7hczKyDtOR4xSbRDxJp7QxK&teks={kelas}{nomor_kelas}&filter=*.html"

        print(url)

        resp = requests.get(url)

        # try:
        soup = BeautifulSoup(resp.text)

        table = soup.find(
            "table",
            {
                "class": "table table-custom table-primary table-fixed bordered-table stacktable large-only"
            },
        )
        if not table:
            break

        trs = table.find_all("tr")

        for tr in trs:
            tds = tr.find_all("td")
            if len(tds) < 1:
                continue

            if tds[1].text.strip() == "Senin":
                parse_date(
                    tds[3].text,
                    senin,
                    tds[0].text,
                    tds[4].text,
                )

            if tds[1].text.strip() == "Selasa":
                parse_date(
                    tds[3].text,
                    selasa,
                    tds[0].text,
                    tds[4].text,
                )
            if tds[1].text.strip() == "Rabu":
                parse_date(
                    tds[3].text,
                    rabu,
                    tds[0].text,
                    tds[4].text,
                )
            if tds[1].text.strip() == "Kamis":
                parse_date(
                    tds[3].text,
                    kamis,
                    tds[0].text,
                    tds[4].text,
                )
            if tds[1].text.strip() == "Jum'at":
                parse_date(
                    tds[3].text,
                    jumat,
                    tds[0].text,
                    tds[4].text,
                )
            if tds[1].text.strip() == "Sabtu":
                parse_date(
                    tds[3].text,
                    sabtu,
                    tds[0].text,
                    tds[4].text,
                )
    return senin, selasa, rabu, kamis, jumat, sabtu


def create_sheet(xlwriter: ExcelWriter, hari_dict: dict, sheet_name: str):
    rows = []
    try:
        od = collections.OrderedDict(sorted(hari_dict.items()))
    except:
        od = hari_dict

    for i in od.keys():
        row = dict({"WAKTU": i}, **od[i])
        rows.append(row)

    df = pd.DataFrame(rows)
    new_order = ["WAKTU", *sorted(df.columns[1:])]
    print(new_order)
    df = df.reindex(new_order, axis=1)
    print(df)
    df.to_excel(xlwriter, sheet_name=sheet_name, index=False)


def read_to_excel(kelas: str):
    senin, selasa, rabu, kamis, jumat, sabtu = scrape_schedule(kelas)
    __import__("pprint").pprint(senin)

    with pd.ExcelWriter(f"Jadwal_{kelas}_Depok.xlsx") as xlwriter:
        create_sheet(xlwriter, senin, "Senin")
        create_sheet(xlwriter, selasa, "Selasa")
        create_sheet(xlwriter, rabu, "Rabu")
        create_sheet(xlwriter, kamis, "Kamis")
        create_sheet(xlwriter, jumat, "Jumat")
        create_sheet(xlwriter, sabtu, "Sabtu")


def main():
    jurusans = ["IA", "KA"]
    for jurusan in jurusans:
        for i in range(1, 5):
            read_to_excel(f"{i}{jurusan}")


if __name__ == "__main__":
    main()
