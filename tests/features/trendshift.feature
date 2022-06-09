Feature: Trend shift reporter

  Scenario: It sums all contiguous trend shifts and sets to 0 the unchanged
    Given an upward shift
    And a few values with no shift
    And a downward shift
    When I ask for the contiguous trend sums
    Then I get a new column with the sum of the cumulative differences

  Scenario: It processes the input dataframe in place
    Given any dataframe
    When I ask for anything in place
    Then it transforms the input dataframe

  Scenario: It returns a transformed copy of the input dataframe
    Given any dataframe
    When I ask for anything not in place
    Then it transforms a copy of the input dataframe

  Scenario: It counts the number of steps for any contiguous value sequence
    Given an upward shift
    And a few values with no shift
    And a downward shift
    When I ask to number every shift step within a trend
    Then I get all trend steps numbered

  Scenario: It calculates the trends simple moving average
    Given an upward shift
    And a few values with no shift
    And a downward shift
    When I ask for the simple moving average for every trend
    Then I get a new column with the simple moving average

  Scenario: It places the total difference from every trend in the first step
    Given an upward shift
    And a few values with no shift
    And a downward shift
    When I ask for the total difference from every trend
    Then I get a new column with the total difference in the first trend step and other steps to null

  Scenario: It places the total number of steps from every trend in the first step
    Given an upward shift
    And a few values with no shift
    And a downward shift
    When I ask for the total steps from every trend
    Then I get a new column with the total number of steps in the first trend step and other steps to null

  Scenario: It executes multiple calculations over all trends
    Given an upward shift
    And a few values with no shift
    And a downward shift
    When I ask for the everything from every trend
    Then I get a new column with the sum of the cumulative differences
    Then I get all trend steps numbered
    Then I get a new column with the simple moving average
    Then I get a new column with the total difference in the first trend step and other steps to null
    Then I get a new column with the total number of steps in the first trend step and other steps to null

  Scenario: It executes multiple calculations over all trends over a massive dataframe
    Given a massive dataframe
    When I ask for the everything from every trend
    Then I get the exact values results

  Scenario: Step number column is an integer number from 0 on
    Given a massive dataframe where a step number bug has been detected
    When I ask for the everything from every trend
    Then I get integers only in the step number column

  Scenario: It finds the trends from a smooth input
    Given an noisy shift with a series of values as "1 3 5 4 7"
    When I ask for the total difference from every trend with a smooth level of 3
    Then I get a total difference with one only upward shift
