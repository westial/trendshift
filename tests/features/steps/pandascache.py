from behave import *
from pandas import Series

from src.trendshift.cache.pandascache import pd_cache

call_count = 0


def increase_call_spy():
    global call_count
    call_count += 1


def reset_call_spy():
    global call_count
    call_count = 0


@given("a basic function decorated with cache")
def step_impl(context):
    @pd_cache
    def multiply_by_2(a_number: int):
        increase_call_spy()
        return a_number * 2
    context.func = multiply_by_2


@when("I call the function twice")
def step_impl(context):
    reset_call_spy()
    context.result1 = context.func(3)
    context.result2 = context.func(3)
    context.expected_result1 = 6
    context.expected_result2 = 6


@then("the function returns the cache of the first call")
def step_impl(context):
    assert 1 == call_count


@when("I call the function twice with different parameter value")
def step_impl(context):
    reset_call_spy()
    context.result1 = context.func(3)
    context.result2 = context.func(2)
    context.expected_result1 = 6
    context.expected_result2 = 4


@then("the function is called twice")
def step_impl(context):
    assert 2 == call_count


@given("a class member function decorated with cache")
def step_impl(context):
    class Complex:
        @classmethod
        @pd_cache
        def operation(cls, a_number, a_title, is_done=True):
            increase_call_spy()
            return f'{3 * a_number} {a_title}' \
                if is_done \
                else f'{a_number} not {a_title}'
    context.complex = Complex()


@step("results are the same")
def step_impl(context):
    assert context.result2 == context.result1
    assert context.expected_result1 == context.result1


@step("results are different")
def step_impl(context):
    assert context.result2 != context.result1
    assert context.expected_result1 == context.result1
    assert context.expected_result2 == context.result2


@when("I call the class member function twice")
def step_impl(context):
    reset_call_spy()
    context.result1 = context.complex.operation(4, "title", False)
    context.result2 = context.complex.operation(4, "title", False)
    context.expected_result1 = "4 not title"
    context.expected_result2 = "4 not title"


@when("I call the class member function twice with a different parameter")
def step_impl(context):
    reset_call_spy()
    context.result1 = context.complex.operation(4, "title", False)
    context.result2 = context.complex.operation(4, "title", True)
    context.expected_result1 = "4 not title"
    context.expected_result2 = "12 title"


@step("results are as expected")
def step_impl(context):
    assert context.expected_result1 == context.result1
    assert context.expected_result2 == context.result2


@given("a function decorated with cache with a Series as argument")
def step_impl(context):
    @pd_cache
    def total_sum_of(a_series: Series):
        increase_call_spy()
        return a_series.sum()
    context.series_func = total_sum_of


@when("I call the function twice with a Series and a copy of this one")
def step_impl(context):
    reset_call_spy()
    a_series = Series([1, 2, 3])
    context.result1 = context.series_func(a_series)
    context.result2 = context.series_func(a_series.copy())
    context.expected_result1 = 6
    context.expected_result2 = 6


@when("I call the function twice with a Series and an updated copy of this one")
def step_impl(context):
    reset_call_spy()
    a_series = Series([1, 2, 3])
    context.result1 = context.series_func(a_series)
    modified = a_series.copy()
    modified.iloc[0] = 3
    context.result2 = context.series_func(modified)
    context.expected_result1 = 6
    context.expected_result2 = 8
