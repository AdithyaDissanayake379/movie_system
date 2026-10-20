from datetime import date
from decimal import Decimal
import pytest
from movie_app.movies import validate as movie_validate
from movie_app.customers import validate as customer_validate
from movie_app.rentals import late_fee

def test_movie_validation():
    assert movie_validate("Alien","Sci-Fi","1979","250","Brandywine")[2] == 1979
    with pytest.raises(ValueError):
        movie_validate("","Sci-Fi",1979,250,"Producer")

def test_customer_validation():
    assert customer_validate("Mary","mary@example.com")[0] == "Mary"
    with pytest.raises(ValueError):
        customer_validate("Mary", "")

def test_late_fee():
    assert late_fee(date(2026,10,10),date(2026,10,13),Decimal("100")) == Decimal("300.00")
    assert late_fee(date(2026,10,10),date(2026,10,9)) == Decimal("0.00")