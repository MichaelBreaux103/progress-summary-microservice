# Test program for the Progress Summary microservice.
# It does NOT import the microservice. It only talks to it over HTTP.
#
# 1. Start the microservice first:   python microservice.py
# 2. Then, in a second terminal:     python test_program.py

import requests

URL = "http://localhost:5002/summary"

tasks = [
    {"title": "Essay", "course": "CS361", "done": True},
    {"title": "Quiz 3", "course": "CS325", "done": False},
    {"title": "Lab 2", "course": "CS361", "done": True},
    {"title": "Reading", "course": "CS361", "done": False},
    {"title": "Homework 5", "course": "CS325", "done": False},
]

# ---------- Test 1: a normal request ----------
print("TEST 1: How much of my work is done?")
print("Sending request to " + URL)

# REQUEST data: send an HTTP POST with a JSON body
response = requests.post(URL, json={
    "records": tasks,
    "status_field": "done",
    "group_field": "course",
})

# RECEIVE data: read the JSON in the response
data = response.json()
print("Status code: " + str(response.status_code))
print("Completed: " + str(data["completed"]) + " of " + str(data["total"]))
print("Remaining: " + str(data["remaining"]))
print("Percent complete: " + str(data["percent_complete"]) + "%")
print("Tasks per course:")
for course in data["groups"]:
    print("  " + course + ": " + str(data["groups"][course]))

# ---------- Test 2: an empty list ----------
print("")
print("TEST 2: Sending an empty list")
response = requests.post(URL, json={"records": [], "status_field": "done"})
print("Status code: " + str(response.status_code))
print("Response: " + str(response.json()))

# ---------- Test 3: a bad request ----------
print("")
print("TEST 3: Sending a bad request (records is missing)")
response = requests.post(URL, json={"status_field": "done"})
print("Status code: " + str(response.status_code))
print("Error message: " + response.json()["error"])
