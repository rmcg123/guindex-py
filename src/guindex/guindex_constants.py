"""Guindex constants."""

api_url = "https://www.guindex.ie/api/"

pubs_url = api_url + "pubs/"
pints_url = api_url + "pubs/{}/prices/"

valid_counties = [
    "Carlow",
    "Cavan",
    "Clare",
    "Cork",
    "Donegal",
    "Dublin",
    "Galway",
    "Kerry",
    "Kildare",
    "Kilkenny",
    "Laois",
    "Leitrim",
    "Limerick",
    "Longford",
    "Louth",
    "Mayo",
    "Meath",
    "Monaghan",
    "Offaly",
    "Roscommon",
    "Sligo",
    "Tipperary",
    "Waterford",
    "Westmeath",
    "Wexford",
    "Wicklow",
]

invalid_query_parameter_message = "Looks like you've had one too many: "
status_not_200_response_message = (
    "Looks like we've had one too many - try back later..."
)
long_request_time_message = (
    "This may take a few minutes - take a seat and "
    "we'll drop the pints over to you..."
)
