import sys
import socket
import ssl
from socket import *

# Name: Aaron Schanz
# V00936095

#sys.tracebacklimit = 0

# Function to parse the input URL
def parse_url(URL):
    protocol = ""
    host = URL
    filepath = ""

    # When URL starts with https://, set protocol
    if URL.startswith("https://"):
        protocol = "https://"
        host = URL[8:]

    # When URL starts with http://, set protocol
    elif URL.startswith("http://"):
        protocol = "http://"
        host = URL[7:]

    # When URL starts with www. or just the domain, set protocol to http://
    else:
        protocol = "http://"
        host = URL

    # Split input into filepath and host 
    try:
        filepath = host.split("/")[1]
        host = host.split("/")[0]
    except IndexError:
        filepath = ""

    return (protocol, host, filepath)

# Function to set port to 443 for SSL or 80 
def get_port(protocol):
    if protocol == "https://":
        return 443
    else:
        return 80
    
# Function to check if website supports http2
def check_http2(host, port):
    try:
        port = 443

        # Create context and set application layer protocol to h2
        ctx = ssl.create_default_context()
        ctx.set_alpn_protocols(['h2'])

        # Connect to host 
        conn = ctx.wrap_socket(socket(AF_INET, SOCK_STREAM), server_hostname = host)
        conn.connect((host, port))

        # if h2 is selected during the request, return yes
        if conn.selected_alpn_protocol() == "h2":
            return "yes"
        else:
            return "no"
        
    # Catch exception and print out function line
    except Exception as e:
        print("Error checking for http2 on line 47: ", e)


def main():
    # Initializing variables
    all_cookies = []
    protected = "no"
    http2_support = "no"
    
    # Function to send request and receive response based on the input
    def handle_request(input):
        # Parsing input for protocol, host and filepath
        protocol, host, filepath = parse_url(input)
    
        # Getting port 
        port = get_port(protocol)

        # Create socket
        try:
            # Variable does not belong to relevant function
            nonlocal http2_support

            #Initializing socket
            s = socket(AF_INET,SOCK_STREAM)
        
            # Connect to given web server using port 80
            if (port == 80):
                s.connect((host, port))

                # Send request
                request = "GET /{} HTTP/1.1\r\nHost: {}\r\n\r\n".format(filepath, host)
                print("---- Request begin ----\n", request, end = '')
                s.send(request.encode('utf-8'))

                print("---- Request end ---- \nHTTP request sent, awaiting response...\n")
            
                # Receive response      
                response = b''  
                while True:
                    chunk = s.recv(1024) 
                    if not chunk:
                        break
                    if b"\r\n\r\n" in chunk:
                        response += chunk.split(b"\r\n\r\n", 1)[0]
                        break
                    response += chunk
                
                s.close()

                # Check for http2 support
                http2_support = check_http2(host, port)

            # Connect to given web server using port 443
            elif (port == 443):
                # Creating context and wrapping socket
                context = ssl.create_default_context()
                conn = context.wrap_socket(s, server_hostname=host)

                conn.connect((host, port))
                
                # Send request 
                request = "GET /{} HTTP/1.1\r\nHost: {}\r\n\r\n".format(filepath, host)
                print("---- Request begin ----\n", request, end = '')
                conn.send(request.encode('utf-8'))

                print("---- Request end ---- \nHTTP request sent, awaiting response...\n")

                # Receive response      
                response = b''  
                while True:
                    chunk = conn.recv(1024) 
                    if not chunk:
                        break
                    if b"\r\n\r\n" in chunk:
                        response += chunk.split(b"\r\n\r\n", 1)[0]
                        break
                    response += chunk

                conn.close()

                # Check for http2 support
                http2_support = check_http2(host, port)

            # If port != 443 | 80, print an error
            else:
                print("Error: Protocol not recognized")
                sys.exit()    

        except Exception as e:
            response = b''
            print("Error trying to connect. Make sure the input URL is a valid website")
            sys.exit()

        # Decoding response to be a string instead of bytes
        try:
            response = response.decode()
            print("---- Response header ----\n" + response + "\n")
        except:
            pass

        # Handling redirects if 301 or 302 are in response
        if ("301 Moved Permanently" in response or "302 Moved Temporarily" in response):
                redirect_location = None
                for header in response.split("\r\n"):

                    # Set redirect location for recursive call
                    if header.startswith("Location: ") or header.startswith("location: "):
                        redirect_location = header[10:].strip()
                        break
                
                #Recursive call to current function
                if redirect_location:
                   handle_request(redirect_location)

        # Separate headers from the body and then split the headers into an array
        headerarray = response.split("\r\n")

        cookies = []
        for header in headerarray:
                # If header starts with Set-Cookie, this means it's a header containing a cookie and add it to the array
                if  header.startswith("Set-Cookie: "):
                    cookies.append(header)

        for cookie in cookies:
            # Variable does not belong to relevant function
            nonlocal all_cookies
            # Separate cookie attributes
            for attribute in cookie.split(";"):

                # If the attribute starts with "Set-Cookie", the name follows
                if attribute.startswith("Set-Cookie: "):
                    index = attribute.find("=")
                    temp = attribute
                    name = temp[12:index]
                    all_cookies += "\ncookie name: " + name

                # if the attribute starts with "expires", the expiry time follows
                if attribute.startswith(" expires="):
                    expiry = attribute[9:]
                    all_cookies += ", expires time: " + expiry

                # if the attribute starts with "domain", the domain name follows
                if attribute.startswith(" domain="):
                    domain = attribute[8:]
                    all_cookies += ", domain name: " + domain

        # Check if website is password protected
        nonlocal protected
        if ("401 Unauthorized" in response or "403 Forbidden" in response):
            protected = "yes"

        return (host, all_cookies, protected)
    
    # Get host, all_cookies and protected in printable format through handle_request function
    host, all_cookies, protected  = handle_request(sys.argv[1])

    print("-- Summary --")   

    #printing the website name 
    try:
        print("website: " + host)
    except IndexError:
        print("Please input a URL")
        sys.exit()
    except Exception as e:
        print("Error, ensure you are entering a valid URL " + e)
        sys.exit()

    # print whether the website supports http2
    print("1. Supports http2: ", http2_support)  
        
    # Print out the list of cookies
    print("2. List of cookies:", end = '')
    for char in all_cookies:
        print(char, end = '')


    # print out whether website is password protected
    print("\n3. Password-protected: " + protected)


if __name__ == "__main__":
    main()
