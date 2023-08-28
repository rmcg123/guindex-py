"""Tests for guindex functions."""

import unittest
from unittest.mock import patch

import pandas as pd
import numpy as np
from pandas.testing import assert_series_equal, assert_frame_equal

from src.guindex import pubs, pints


class TestPubs(unittest.TestCase):
    """Test for pubs function from src.guindex.py."""

    def setUp(self) -> None:

        self.response = pd.DataFrame(
            data={
                "id": list(range(4)),
                "creationDate": [
                    "2020-01-01T12:00:00Z",
                    "2020-01-02T12:00:00Z",
                    "2020-01-01T12:00:00.12345Z",
                    "2020-01-01T12:00:00.67890Z",
                ],
                "name": ["Bar", "Pub", "Tavern", "Night Club"],
                "county": ["Carlow", "Limerick", "Mayo", "Cavan"],
                "longitude": ["-6.89", "-8.62", "-9.37", "-7.36"],
                "latitude": ["52.76", "52.6", "53.9", "53.98"],
                "mapLink": ["map_url1", "map_url2", "map_url3", "map_url4"],
                "closed": [False, False, False, False],
                "servingGuinness": [True, True, True, True],
                "lastPrice": ["4.3", "4.7", None, "5.1"],
                "lastSubmissionTime": [
                    "2021-01-01T12:00:00Z",
                    "2021-01-02T12:00:00Z",
                    "2021-01-01T12:00:00.12345Z",
                    "2021-01-01T12:00:00.67890Z",
                ],
                "averageRating": ["2.4", "4.0", None, "1.6"],
                "creator": [np.nan, 1.0, 2.0, 3.0],
            }
        )

    def validate_pubs_args(self):
        """Check parameter checks are working."""

        with self.assertRaises(ValueError):
            pubs(county="FakeCounty")

        with self.assertRaises(ValueError):
            pubs(closed="Maybe")

        with self.assertRaises(ValueError):
            pubs(serving_guinness="don't know")

    @patch("src.guindex.pubs_request")
    def test_pubs(self, mock_pubs_request):
        """Check that data formatting is working."""

        mock_pubs_request.return_value = self.response

        result = pubs()

        with self.subTest("Test columns"):
            result_1 = list(result.columns)
            expected = [
                "pub_id",
                "creation_date",
                "name",
                "county",
                "longitude",
                "latitude",
                "map_link",
                "closed",
                "serving_guinness",
                "last_price",
                "last_submission_time",
                "average_rating",
                "pub_creator_id",
            ]

            assert result_1 == expected

        with self.subTest("Test longitude"):
            result_2 = result["longitude"].to_list()
            expected = [-6.89, -8.62, -9.37, -7.36]

            assert result_2 == expected

        with self.subTest("Test latitude"):
            result_3 = result["latitude"].to_list()
            expected = [52.76, 52.6, 53.9, 53.98]

            assert result_3 == expected

        with self.subTest("Test last price"):
            result_4 = result["last_price"]
            expected = pd.Series([4.3, 4.7, np.nan, 5.1], name="last_price")

            assert_series_equal(result_4, expected)

        with self.subTest("Test average rating"):
            result_5 = result["average_rating"]
            expected = pd.Series(
                [2.4, 4.0, np.nan, 1.6], name="average_rating"
            )

            assert_series_equal(result_5, expected)

        with self.subTest("Test creation date"):
            result_6 = result["creation_date"].to_list()
            expected = [
                pd.Timestamp("2020-01-01 12:00:00Z"),
                pd.Timestamp("2020-01-02 12:00:00Z"),
                pd.Timestamp("2020-01-01 12:00:00.12345Z"),
                pd.Timestamp("2020-01-01 12:00:00.67890Z"),
            ]

            assert result_6 == expected

        with self.subTest("Test last submission time"):
            result_7 = result["last_submission_time"].to_list()
            expected = [
                pd.Timestamp("2021-01-01 12:00:00Z"),
                pd.Timestamp("2021-01-02 12:00:00Z"),
                pd.Timestamp("2021-01-01 12:00:00.12345Z"),
                pd.Timestamp("2021-01-01 12:00:00.67890Z"),
            ]

            assert result_7 == expected

        with self.subTest("Test with prices parameter"):
            result_8 = result.loc[
                result["last_price"].notnull(), :
            ].reset_index(drop=True)
            expected = self.response.loc[[0, 1, 3]].reset_index(drop=True)

            assert_frame_equal(result_8, expected)


class TestPints(unittest.TestCase):
    """Test for pints function from src.guindex.py."""

    def setUp(self) -> None:

        self.pubs_response = pd.DataFrame(
            data={
                "pub_id": list(range(2)),
                "creation_date": [
                    pd.Timestamp("2020-01-01T12:00:00Z"),
                    pd.Timestamp("2020-01-02T12:00:00Z"),
                ],
                "name": ["Bar", "Pub"],
                "county": ["Carlow", "Limerick"],
                "longitude": [-6.89, -8.62],
                "latitude": [52.76, 52.6],
                "map_link": ["map_url1", "map_url2"],
                "closed": [False, False],
                "serving_guinness": [True, True],
                "last_price": [4.3, 4.7],
                "last_submission_time": [
                    pd.Timestamp("2021-01-01T12:00:00Z"),
                    pd.Timestamp("2021-01-02T12:00:00Z"),
                ],
                "average_rating": ["2.4", "4.0"],
                "creator": [np.nan, 1.0],
            }
        )

        self.pints1_response = pd.DataFrame(
            data={
                "id": [10, 12],
                "creationDate": [
                    "2020-05-02T12:00:00Z",
                    "2021-01-01T12:00:00Z",
                ],
                "price": ["4.2", "4.3"],
                "starRating": [np.nan, 3.0],
                "creator": [2, 4],
                "pub": [0, 0],
            }
        )

        self.pints2_response = pd.DataFrame(
            data={
                "id": [11, 14],
                "creationDate": [
                    "2020-05-02T12:00:00Z",
                    "2021-01-02T12:00:00Z",
                ],
                "price": ["4.5", "4.7"],
                "starRating": [4.0, 3.0],
                "creator": [2, 4],
                "pub": [1, 1],
            }
        )

    @patch("src.guindex.pints_request")
    @patch("src.guindex.pubs")
    def test_pints(self, mock_pubs, mock_pints_request):

        mock_pubs.return_value = self.pubs_response

        mock_pints_request.side_effect = [
            self.pints1_response,
            self.pints2_response,
        ]

        result = pints()

        with self.subTest("Test columns"):

            result_1 = list(result.columns)

            expected = [
                "pint_id",
                "creation_date",
                "price",
                "star_rating",
                "pint_creator_id",
                "pub_id",
                "name",
                "county",
                "longitude",
                "latitude",
            ]

            assert result_1 == expected

        with self.subTest("Test creation dates"):

            result_2 = result["creation_date"].to_list()

            expected = [
                pd.Timestamp("2020-05-02T12:00:00Z"),
                pd.Timestamp("2021-01-01T12:00:00Z"),
                pd.Timestamp("2020-05-02T12:00:00Z"),
                pd.Timestamp("2021-01-02T12:00:00Z"),
            ]

            assert result_2 == expected

        with self.subTest("Test prices"):

            result_3 = result["price"].to_list()

            expected = [4.2, 4.3, 4.5, 4.7]

            assert result_3 == expected

        with self.subTest("Test names"):

            result_4 = result["name"].to_list()

            expected = ["Bar", "Bar", "Pub", "Pub"]

            assert result_4 == expected

        with self.subTest("Test counties"):

            result_5 = result["county"].to_list()

            expected = ["Carlow", "Carlow", "Limerick", "Limerick"]

            assert result_5 == expected


if __name__ == "__main__":
    unittest.main()
