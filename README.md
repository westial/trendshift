TrendShift
==========

TrendShift is a builder-like library that appends some trend aggregations about
onto a given pandas DataFrame.

In the following image the blue line, with the value on the right side, draws
the EUR/USD price along a few hours and the red line, with the value on the
left,
draws the difference between every price movement, the trends.

![https://westial.com/eurusdtrends.png](https://westial.com/eurusdtrends.png)

## Install ##

```
pip install trendshift
```

## Usage ##

The following example implementation builds all the available TrendShift
features for a dataframe in the column "target_column".

```
my_new_df: DataFrame = = TrendShift(input_dataframe, "target_column")\
    .with_sum()\
    .with_numbered_steps()\
    .with_simple_moving_avg()\
    .with_steps_by_trend()\
    .with_difference_by_trend()\
    .with_trend_countdown()\
    .build()
```

The snippet above over an example "input_dataframe.target_column" will output
the following data set. "target_column" values are the original ones.

|     | target_column |trends_sum|step_number|simple_moving_avg  |trend_difference|trend_steps| trend_countdown |
|-----|---------------|----------|-----------|-------------------|----------------|-----------|-----------------|
| 0   | 1             |          |           |0.0                |                |           |                 |
| 1   | 16            |15.0      |1.0        |15.0               |20.0            |2.0        | 2.0             |
| 2   | 21            |20.0      |2.0        |10.0               |                |           | 1.0             |
| 3   | 21            |0.0       |0.0        |0.0                |                |           | 0.0             |
| 4   | 21            |0.0       |0.0        |0.0                |                |           | 0.0             |
| 5   | 21            |0.0       |0.0        |0.0                |                |           | 0.0             |
| 6   | 20            |-1.0      |1.0        |-1.0               |-11.0           |3.0        | 3.0             |
| 7   | 17            |-4.0      |2.0        |-2.0               |                |           | 2.0             |
| 8   | 10            |-11.0     |3.0        |-3.6666666666666665|                |           | 1.0             |

More information within the main interface [src/trendshift/trendshift.py](src/trendshift/trendshift.py)

## Concepts ##

### Trend ###

A *Trend* is a pattern found in incremental or at least continuous series
datasets, like for example time series, that describes whether the data is
moving upward or downward.

### Shift ###

A *Shift* is a group of states within the input series dataset in one only
direction, upward or downward. When the trend of the next value is different
from the current one, the current *Shift* ends and the next *Shift* starts in
the following value.

### Step ###

A *Step* is a state in the dataset series during an upward or downward *Shift*.
A step of the input dataframe is a row within a *Shift*.

## Features ##

TrendShift applies some cumulative calculations over the target column. It
appends a column for every calculation as a result to the original DataFrame.

### Sum ###

Cumulative sum of every *Step* in a *Shift*.

### Numbered Step ###

Cumulative *Step* count of every *Shift*.

### SMA ###

Simple Moving Average is the average of the difference between all *Step* in
a *Shift*.

### Trend Difference ###

Total difference between the first *Step* and the last one in a *Shift*. This
value is placed in the first *Step* only.

### Trend Steps ###

Total number of *Step* in a *Shift*. This value is placed in the first *Step*
only.

### Trend Countdown ###

Reversed upside down cumulative *Step* count in a *Shift*.

## Test ##

Tests are an important part in this project. My developing methodology is BDD
and I developed this whole project from [tests/features](tests/features).

There you can find the most specific documentation about any service or entity
of this project.

If you are not only a user of this library but a developer who wants to adapt or
maintain this code, you should follow the same way, BDD.

The package <https://behave.readthedocs.io/> is a development dependency you
must install.

```
pip install behave
```

Execute the tests by the following command:

```
behave tests/features
```

## Author ##

Jaume Mila Bea <jaume@westial.com>