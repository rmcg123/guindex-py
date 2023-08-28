# Guindex Package
This package retrieves data from the Guindex project for various end-uses. 
The Guindex is a community data-collection project that tracks the price of 
pints of Guinness in pubs across the Republic of Ireland. More information 
on the Guindex project is available 
[here](https://www.guindex.ie).

## Installation
This package can be installed through `pip install guindex`.

## Quick Start Examples:
Below are some examples of using the package:
1. Return a Pandas DataFrame that has all of the pubs from the Guindex 
   project:
    ```
    import guindex
    
    pubs_df = guindex.pubs()
    ```
2. Return a Pandas DataFrame that has all open pubs from county Wicklow that 
   have 
   a price of Guinness submitted:
    ```
    import guindex
    
    pubs_df = guindex.pubs(county="Wicklow", closed=False, with_prices=True)
    ```
3. Return a Pandas DataFrame that has all of the Guinness prices that have 
   been submitted to the Guindex:
   ```
   import guindex
   
   pints_df = guindex.pints()
   ```