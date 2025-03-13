import sqlite_utils

db = sqlite_utils.Database("local.db")

db["album"].create({
    "id": int,
    "title": str,
    "image": str,
    "season": str,
    "date": str,
    "gps": tuple,
    "address": str
}, pk="id")

