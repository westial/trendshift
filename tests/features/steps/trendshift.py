import numpy as np
import pandas as pd
from behave import *
from pandas import DataFrame

from src.trendshift.trendshift import TrendShift


def __create_data_frame_with_diff(values):
    data_frame = DataFrame({"samples": values})
    return data_frame


@given("an upward shift")
def step_impl(context):
    context.data_frame_values = [1, 16, 21]
    context.expected_diff_sum = [np.nan, 15, 20]
    context.expected_diff_count = [np.nan, 1, 2]
    context.expected_diff_speed = [0, 15, 10]
    context.expected_total_differences = [np.nan, 20, np.nan]
    context.expected_total_steps_count = [np.nan, 2, np.nan]


@step("a few values with no shift")
def step_impl(context):
    context.data_frame_values += [21, 21, 21]
    context.expected_diff_sum += [0, 0, 0]
    context.expected_diff_count += [0, 0, 0]
    context.expected_diff_speed += [0, 0, 0]
    context.expected_total_differences += [np.nan, np.nan, np.nan]
    context.expected_total_steps_count += [np.nan, np.nan, np.nan]


@step("a downward shift")
def step_impl(context):
    context.data_frame_values += [20, 17, 10]
    context.expected_diff_sum += [-1, -4, -11]
    context.expected_diff_count += [1, 2, 3]
    context.expected_diff_speed += [-1, -2, -3]
    context.expected_total_differences += [-11, np.nan, np.nan]
    context.expected_total_steps_count += [3, np.nan, np.nan]
    context.data_frame = __create_data_frame_with_diff(
        context.data_frame_values)


@step("any dataframe")
def step_impl(context):
    context.data_frame = __create_data_frame_with_diff([20, 17, 10])


@when("I ask for the contiguous trend sums")
def step_impl(context):
    context.result = TrendShift(context.data_frame, "samples") \
        .with_sum() \
        .build()


@then("I get a new column with the sum of the cumulative differences")
def step_impl(context):
    assert np.array_equal(
        np.array(context.expected_diff_sum).astype(int),
        np.array(context.result["trends_sum"]).astype(int)
    )


@when("I ask to number every shift step within a trend")
def step_impl(context):
    context.result = TrendShift(context.data_frame, "samples") \
        .with_numbered_steps() \
        .build()


@then("I get all trend steps numbered")
def step_impl(context):
    assert np.array_equal(
        np.array(context.expected_diff_count).astype(int),
        np.array(context.result["step_number"]).astype(int)
    )


@when("I ask for the simple moving average for every trend")
def step_impl(context):
    context.result = TrendShift(context.data_frame, "samples") \
        .with_simple_moving_avg() \
        .build()


@then("I get a new column with the simple moving average")
def step_impl(context):
    assert np.array_equal(
        np.array(context.result["simple_moving_avg"]).astype(np.int),
        np.array(context.expected_diff_speed)
    )


@when("I ask for the total difference from every trend")
def step_impl(context):
    context.result = TrendShift(context.data_frame, "samples") \
        .with_difference_by_trend() \
        .build()


@then(
    "I get a new column with the total difference in the first trend step and other steps to null")
def step_impl(context):
    assert np.array_equal(
        np.array(context.expected_total_differences).astype(int),
        np.array(context.result["trend_difference"]).astype(int)
    )


@when("I ask for the total steps from every trend")
def step_impl(context):
    context.result = TrendShift(context.data_frame, "samples") \
        .with_steps_by_trend() \
        .build()


@then(
    "I get a new column with the total number of steps in the first trend step and other steps to null")
def step_impl(context):
    assert np.array_equal(
        np.array(context.expected_total_steps_count).astype(int),
        np.array(context.result["trend_steps"]).astype(int)
    )


@when("I ask for the everything from every trend")
def step_impl(context):
    context.result = TrendShift(context.data_frame, "samples") \
        .with_sum() \
        .with_numbered_steps() \
        .with_simple_moving_avg() \
        .with_steps_by_trend() \
        .with_difference_by_trend() \
        .build()


@when("I ask for anything in place")
def step_impl(context):
    context.result = TrendShift(context.data_frame, "samples", in_place=True) \
        .with_steps_by_trend() \
        .build()


@then("it transforms the input dataframe")
def step_impl(context):
    assert context.data_frame is context.result


@when("I ask for anything not in place")
def step_impl(context):
    context.result = TrendShift(context.data_frame, "samples") \
        .with_steps_by_trend() \
        .build()


@then("it transforms a copy of the input dataframe")
def step_impl(context):
    assert context.data_frame is not context.result


@given("a massive dataframe")
def step_impl(context):
    df = pd.read_parquet("tests/sample/live15m.parquet").sort_index()
    df = df.loc[~df.index.duplicated(), :]
    df['samples'] = df['close']
    context.data_frame = df[['samples']]


def assert_all_columns_sum_the_same_from(df1, df2):
    sum1 = df1.sum()
    sum2 = df2.sum()
    np.testing.assert_almost_equal(sum1["samples"], sum2["samples"], decimal=5)
    np.testing.assert_almost_equal(sum1["trends_sum"], sum2["trends_sum"], decimal=5)
    np.testing.assert_almost_equal(sum1["step_number"], sum2["step_number"], decimal=5)
    np.testing.assert_almost_equal(sum1["simple_moving_avg"], sum2["simple_moving_avg"], decimal=5)
    np.testing.assert_almost_equal(sum1["trend_difference"], sum2["trend_difference"], decimal=5)
    np.testing.assert_almost_equal(sum1["trend_steps"], sum2["trend_steps"], decimal=5)


@then("I get the exact values results")
def step_impl(context):
    df = context.result
    expected = pd.read_parquet("tests/sample/live15m_expected.parquet")
    assert_all_columns_sum_the_same_from(df, expected)
