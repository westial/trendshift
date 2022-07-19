import numpy as np
from pandas import DataFrame, Series


class TrendShift:
    """
    TrendShift is implemented following the builder pattern. It is instantiated
    with an input pandas DataFrame and the name of the target column in this
    DataFrame that watches on.

    The modification of the input dataframe in place is an option of the
    constructor as well.

    Most of the member functions are decorated with a result cache to avoid the
    same operation onto the same data twice.
    """

    # The precision decimals to take in account when comparing float numbers.
    PRECISION_DECIMALS = 10

    def __init__(self, df: DataFrame, target_column: str, in_place=False,
                 smooth: int = None, diff_periods=1):
        """
        TrendShift constructor. All calculations are based on the difference
        between steps along the target column.
        :param diff_periods:
        :param df: input dataframe
        :param target_column: target column in the dataframe
        :param in_place: whether create or not the new columns with the trend
        information.
        :param smooth: level of smoothness of the difference between steps.
        The smooth is applied by a moving average calculation and this value
        is the number of steps within the window.
        :param diff_periods: number of steps back to calculate the difference
        between steps. 1 by default means the difference is calculated between
        the current step and the contiguous back one.
        """
        self.__df = df if in_place else df.copy()
        self.__target_diff = self.__create_target_diff(
            df, target_column, smooth, diff_periods)
        self.__sum = False
        self.__numbered_steps = False
        self.__sma = False
        self.__diff_by_trend = False
        self.__steps_by_trend = False
        self.__trend_countdown = False

    @classmethod
    def __create_target_diff(cls, df, column_name, smooth, periods):
        column = df[column_name]
        if None is not smooth:
            column = column.rolling(window=smooth).mean()
        return column.diff(periods)

    def with_numbered_steps(self):
        """
        Building option to append a column for numbered steps for every trend.

        The column name is "step_number".
        """
        self.__numbered_steps = True
        return self

    def with_sum(self):
        """
        Building option to append a column for the cumulative sum of every
        step in a shift. The first difference is added to the second step
        difference, the third to the second, and so on.

        The column name is "trends_sum".
        """
        self.__sum = True
        return self

    def with_simple_moving_avg(self):
        """
        Building option to append a column for the simple moving average into 
        the product.

        The column name is "simple_moving_avg".
        """
        self.__sma = True
        return self

    def with_difference_by_trend(self):
        """
        Building option to append a column with a value only in the first step
        of every trend. This value is the total difference of the trend, from
        the first step to the last. Only the first step in a trend has a value,
        the other steps are NaN.

        The column name is "trend_difference".
        """
        self.__diff_by_trend = True
        return self

    def with_steps_by_trend(self):
        """
        Building option to append the column with a value only in the first step
        of every trend. This value is the total number of steps of the trend.
        Only the first step in a trend has a value the other steps are NaN.

        The column name is "trend_steps".
        """
        self.__steps_by_trend = True
        return self

    def with_trend_countdown(self):
        """
        Building option to append a column for a countdown of the numbered
        steps for every trend.

        The column name is "trend_countdown".
        """
        self.__trend_countdown = True
        return self

    def build(self):
        """
        Building method to create the dataframe according all building options
        described above.
        """
        if self.__sum:
            self.__df["trends_sum"] = self.__sum_steps_from(self.__target_diff)
        if self.__numbered_steps:
            self.__df["step_number"] = \
                self.__number_steps_from(self.__target_diff)
        if self.__sma:
            self.__df["simple_moving_avg"] = \
                self.__calculate_sma_from(self.__target_diff)
        if self.__diff_by_trend:
            self.__df["trend_difference"] = \
                self.total_trend_diff_from(self.__target_diff)
        if self.__steps_by_trend:
            self.__df["trend_steps"] = \
                self.count_trend_steps_from(self.__target_diff)
        if self.__trend_countdown:
            self.__df["trend_countdown"] = \
                self.countdown_trend_steps_from(self.__target_diff)
        return self.__df

    @classmethod
    def count_trend_steps_from(cls, a_series: Series):
        return cls.__involute_total_trend(a_series, cls.__count_reversed_from)

    @classmethod
    def countdown_trend_steps_from(cls, a_series: Series):
        return cls.__involute_trend_transition(a_series, cls.__count_reversed_from)

    @classmethod
    def total_trend_diff_from(cls, a_series: Series):
        return cls.__involute_total_trend(a_series, cls.__sum_reversed_from)

    @classmethod
    def __sum_reversed_from(cls, a_series: Series):
        return cls.__sum_steps_from(
            a_series.sort_index(ascending=False)
        ).sort_index(ascending=True)

    @classmethod
    def __count_reversed_from(cls, a_series: Series):
        return cls.__number_steps_from(
            a_series.sort_index(ascending=False)
        ).sort_index(ascending=True)

    @classmethod
    def __involute_total_trend(cls, a_series: Series, callback: callable):
        sandbox = cls.__involute(a_series, callback)
        sandbox["reversed"].loc[sandbox["count"] != 1] = np.nan
        return sandbox["reversed"]

    @classmethod
    def __involute_trend_transition(cls, a_series: Series, callback: callable):
        sandbox = cls.__involute(a_series, callback)
        return sandbox["reversed"]

    @classmethod
    def __involute(cls, a_series: Series, callback: callable):
        sandbox = DataFrame(index=a_series.index)
        sandbox["count"] = cls.__number_steps_from(a_series)
        sandbox["reversed"] = callback(a_series)
        return sandbox

    @classmethod
    def __calculate_sma_from(cls, a_series: Series):
        column_clone = a_series.copy()
        up_sma = cls.__sma_from(
            cls.__sum_ascending_from(column_clone),
            cls.__number_ascending_from(column_clone))
        down_sma = cls.__sma_from(
            cls.__sum_descending_from(column_clone),
            cls.__number_descending_from(column_clone))
        column_clone.replace([np.nan, np.any], 0, inplace=True)
        column_clone.update(up_sma)
        column_clone.update(down_sma)
        return column_clone

    @classmethod
    def __number_steps_from(cls, a_series: Series):
        column_clone = cls.__reset(a_series.copy())
        column_clone.update(cls.__number_ascending_from(a_series))
        column_clone.update(cls.__number_descending_from(a_series))
        return column_clone

    @classmethod
    def __reset(cls, a_series):
        return a_series.where(((a_series == 0) | a_series.isnull()), 0)

    @classmethod
    def __sum_steps_from(cls, a_series: Series):
        column_clone = cls.__reset(a_series.copy())
        up_sum = cls.__sum_ascending_from(a_series)
        down_sum = cls.__sum_descending_from(a_series)
        column_clone.update(up_sum)
        column_clone.update(down_sum)
        return column_clone

    @classmethod
    def __set_not_null_to_1_from(cls, a_series: Series):
        """
        It sets any not null value to 1 and everything else to null
        """
        return a_series.notna().astype(int).replace(0, np.nan)

    @classmethod
    def __set_ascending_to_1_from(cls, a_series: Series):
        return cls.__set_not_null_to_1_from(
            cls.__ascending_trends_from(a_series))

    @classmethod
    def __set_descending_to_1_from(cls, a_series: Series):
        return cls.__set_not_null_to_1_from(
            cls.__descending_trends_from(a_series))

    @classmethod
    def __number_ascending_from(cls, a_series: Series):
        return cls.__sum_consecutive_from(
            cls.__set_ascending_to_1_from(a_series))

    @classmethod
    def __number_descending_from(cls, a_series: Series):
        return cls.__sum_consecutive_from(
            cls.__set_descending_to_1_from(a_series))

    @classmethod
    def __sum_ascending_from(cls, a_series: Series):
        return cls.__sum_consecutive_from(
            cls.__ascending_trends_from(a_series))

    @classmethod
    def __sum_descending_from(cls, a_series: Series):
        return cls.__sum_consecutive_from(
            cls.__descending_trends_from(a_series))

    @classmethod
    def __sum_consecutive_from(cls, a_series):
        cumulative_sum = a_series.cumsum().fillna(method='pad')
        reset = -cumulative_sum[a_series.isnull()].diff().fillna(cumulative_sum)
        result = a_series.where(a_series.notnull(), reset).cumsum()
        return result[0 != result.round(decimals=cls.PRECISION_DECIMALS)]

    @classmethod
    def __ascending_trends_from(cls, a_series: Series):
        return a_series.mask(a_series <= 0)

    @classmethod
    def __descending_trends_from(cls, a_series: Series):
        return a_series.mask(a_series >= 0)

    @classmethod
    def __sma_from(cls, distance, steps_count):
        return distance / steps_count
