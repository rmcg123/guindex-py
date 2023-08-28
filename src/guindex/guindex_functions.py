"""Functions for guindex package."""
import time
import random

import requests
import pandas as pd

from guindex.guindex_constants import (
    pubs_url,
    pints_url,
    valid_counties,
    invalid_query_parameter_message,
    status_not_200_response_message,
    long_request_time_message,
)


def pubs_request(pub_info_url, query_params):
    """Function to send the API request and to retrieve the pubs data."""

    # Submit GET Request to pubs URL.
    response = requests.get(pub_info_url, params=query_params)

    if response.status_code != 200:
        print(status_not_200_response_message)
    else:
        response = response.json()

        # Results may be paginated, if so get all necessary pages.
        pub_df = pd.json_normalize(response["results"])
        while response["next"]:
            response = requests.get(response["next"], params=query_params)

            if response.status_code != 200:
                print(status_not_200_response_message)
            else:
                response = response.json()
                next_pubs = pd.json_normalize(response["results"])

                # Add pubs as we go.
                pub_df = pd.concat([pub_df, next_pubs], ignore_index=True)

                time.sleep(0.1 * random.random())

        return pub_df


def pubs(county=None, serving_guinness=None, closed=None, with_prices=False):
    """
    Function to retrieve all pubs information from the Guindex API.

    parameters
    ----------
    county: str, default None
        Whether to select a particular county to retrieve pubs from.
        Specifying None will return pubs from all 26 counties.
    serving_guinness: bool, default None
        Whether to only retrieve pubs that do or do not serve guinness.
        Specifying None will return both types of pubs.
    closed: bool, default None
        Whether to only retrieve pubs that are closed or open.
        Specifying None will return both types of pubs.
    with_prices: bool, default False
        Whether to only return pubs that have had a price submitted.
        Specifying False will return all pubs.

    Returns
    -------
    pub_df: pd.DataFrame
        A pandas DataFrame with the requested pubs information.
    """

    print("Retrieving pubs information...")

    # Set up and validate parameters for HTTP Request.
    query_params = {}
    if county:
        if county not in valid_counties:
            raise ValueError(
                invalid_query_parameter_message
                + f"county {county} is not in valid counties: {valid_counties}"
            )
        query_params["county"] = county
    if serving_guinness:
        if isinstance(serving_guinness, bool):
            serving_guinness = str(serving_guinness)
        if serving_guinness not in ["True", "False"]:
            raise ValueError(
                invalid_query_parameter_message + f"serving"
                f"_guinness {serving_guinness} must be"
                f"one of ['True', 'False']"
            )
        query_params["servingGuinness"] = serving_guinness
    if closed:
        if isinstance(closed, bool):
            closed = str(closed)
        if closed not in ["True", "False"]:
            raise ValueError(
                invalid_query_parameter_message + f"closed {closed} "
                f"must be one of ['True', 'False']"
            )
        query_params["closed"] = closed

    # Send pubs request to Guindex API.
    pub_df = pubs_request(pub_info_url=pubs_url, query_params=query_params)

    # Adjust naming of columns to snake case.
    old_cols = list(pub_df.columns)
    new_cols = []
    for col in old_cols:
        new_col_str = ""
        for char in col:
            if char.isupper():
                char = "_" + char.lower()
            new_col_str = new_col_str + char
        new_cols.append(new_col_str)

    pub_df.rename(columns=dict(zip(old_cols, new_cols)), inplace=True)

    # Make sure float columns return the correct data type.
    float_cols = ["longitude", "latitude", "last_price", "average_rating"]
    pub_df[float_cols] = pub_df[float_cols].astype(float)

    # Make sure datetime columns return the correct data type.
    for datetime_col in ["creation_date", "last_submission_time"]:
        pub_df[datetime_col] = pd.to_datetime(
            pub_df[datetime_col], format="%Y-%m-%dT%H:%M:%S%z"
        )

    # Make sure pub creator IDs are integers.
    pub_df["creator"] = pub_df["creator"].astype("Int64")

    # Option to filter only pubs that have had a price of Guinness submitted.
    if with_prices:
        pub_df = pub_df.loc[pub_df["last_price"].notnull(), :].reset_index(
            drop=True
        )

    # Rename columns for clarity.
    pub_df.rename(
        columns={"id": "pub_id", "creator": "pub_creator_id"}, inplace=True
    )

    return pub_df


def pints_request(pub_pint_url):
    """Function to send the API request and to retrieve the pints data."""

    # Submit GET request to pints url for selected pub.
    response = requests.get(pub_pint_url)

    if response.status_code != 200:
        print(status_not_200_response_message)
    else:
        response = response.json()
        # Results may be paginated, if so get all required pages.
        pub_pints_df = pd.json_normalize(response["results"])
        while response["next"]:
            response = requests.get(response["next"])

            if response.status_code != 200:
                print(status_not_200_response_message)
            else:
                response = response.json()
                next_pub_pints = pd.json_normalize(response["results"])

                # Add pints as we go.
                pub_pints_df = pd.concat(
                    [pub_pints_df, next_pub_pints], ignore_index=True
                )

                time.sleep(0.01 * random.random())

        return pub_pints_df


def pints(county=None):
    """
    Function to retrieve all pints information from the Guindex API.

    Parameters
    ----------
    county: str, default None
        Whether to only retrieve the pints information for pubs from a
        selected county. Specifying None will retrieve pints from pubs from
        all counties.

    Returns
    -------
    pints_df: pd.DataFrame
        A pandas DataFrame with the retrieved pints information.
    """

    print("Retrieving pints information...")

    # Determine which pubs have had pint prices submitted.
    pubs_with_prices_df = pubs(county=county, with_prices=True)
    pubs_with_prices_ids = pubs_with_prices_df["pub_id"].to_list()

    if len(pubs_with_prices_ids) > 100:
        print(long_request_time_message)

    # For each pub with at least one pint submitted get all of the pint
    # submissions.
    pints_df = pd.DataFrame()
    for pub_id in pubs_with_prices_ids:

        # Select pints url for pub and retrieve pints.
        pub_pint_url = pints_url.format(pub_id)
        pub_pints_df = pints_request(pub_pint_url)

        # Add pints to accruing dataset.
        pints_df = pd.concat([pints_df, pub_pints_df], ignore_index=True)

    # Adjust naming of columns to snake case.
    old_cols = list(pints_df.columns)
    new_cols = []
    for col in old_cols:
        new_col_str = ""
        for char in col:
            if char.isupper():
                char = "_" + char.lower()
            new_col_str = new_col_str + char
        new_cols.append(new_col_str)

    pints_df.rename(columns=dict(zip(old_cols, new_cols)), inplace=True)

    # Correctly format datetime columns.
    pints_df["creation_date"] = pd.to_datetime(
        pints_df["creation_date"], format="%Y-%m-%dT%H:%M:%S%z"
    )

    # Correctly format float columns.
    pints_df["price"] = pints_df["price"].astype(float)

    # Rename columns for clarity.
    pints_df.rename(
        columns={
            "id": "pint_id",
            "creator": "pint_creator_id",
            "pub": "pub_id",
        },
        inplace=True,
    )

    # Merge pub information into pints dataset.
    pints_df = pints_df.merge(
        pubs_with_prices_df[
            ["pub_id", "name", "county", "longitude", "latitude"]
        ],
        how="left",
        on="pub_id",
    )

    return pints_df
