To run SmartClient.py correctly, please follow these steps:
    1: Ensure you are using Python3
    2: Run the following command: python3 SmartClient.py [input]
    3: [input] should take one of the four following forms:
        - www.example.com
        - example.com
        - https://www.example.com
        - http://www.example.com

Now you will see some output on the CLI.

The first part will be marked by a line saying "----  Request begin ----"
Underneath this part the request will be printed.

Then there is a line saying "---- Request end ----"
This line just signifies that the request has been sent and we are waiting for the response

Then there is a line saying "---- Response Header ----"
Underneath this line the HTTP response is printed in a decoded, string format.
Oftentimes the request and response are printed multiple times, when a 301 or 302 code is present and a redirect happens.
It's much easier to understand what's going on in the code if the response and request is printed per each redirect, so I kept it like this.

The most important part is the Summary located below the line that says "-- Summary --"
It will be of this format:
    website: www.example.com             ----- this is the host of the input
    1. Supports http2:  no / yes         ----- this is a boolean whether the input URL supports http2
    2. List of cookies: [Cookie list]    ----- A list of cookies will be printed here
    3. Password-protected: no / yes      ----- this is a boolean whether the input URL is password protected or not 
