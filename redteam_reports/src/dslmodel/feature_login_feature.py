
# feature_login_feature.py

"""
Generated
pytest - bdd
tests
for the feature: Login Feature
"""

import pytest
from pytest_bdd import scenarios, given, when, then, parsers

# Scenarios

scenarios("Successful Login")

scenarios("Failed Login")


# Steps

# Successful Login

@given('User is on the login page')

def step_impl_1():
    pass


@when('User enters correct username and password')

def step_impl_2():
    pass


@then('User is logged in successfully')

def step_impl_3():
    pass



# Failed Login

@given('User is on the login page')

def step_impl_1():
    pass


@when('User enters incorrect username and password')

def step_impl_2():
    pass


@then('User is not logged in')

def step_impl_3():
    pass


