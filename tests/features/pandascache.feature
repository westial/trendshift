Feature: Pandas cache decorator

  Scenario: It caches a function result
    Given a basic function decorated with cache
    When I call the function twice
    Then the function returns the cache of the first call
    And results are as expected

  Scenario: It does not cache a call to a function with different parameters
    Given a basic function decorated with cache
    When I call the function twice with different parameter value
    Then the function is called twice
    And results are as expected

  Scenario: It caches a complex function result
    Given a class member function decorated with cache
    When I call the class member function twice
    Then the function returns the cache of the first call
    And results are as expected

  Scenario: It does not cache a complex function with different parameters
    Given a class member function decorated with cache
    When I call the class member function twice with a different parameter
    Then the function is called twice
    And results are as expected

  Scenario: It caches a function result with a Series as argument
    Given a function decorated with cache with a Series as argument
    When I call the function twice with a Series and a copy of this one
    Then the function returns the cache of the first call
    And results are as expected

  Scenario: It does not cache a function result with a different Series as argument
    Given a function decorated with cache with a Series as argument
    When I call the function twice with a Series and an updated copy of this one
    Then the function is called twice
    And results are as expected