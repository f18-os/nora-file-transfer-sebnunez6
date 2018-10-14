#Server Thread
Server thread will create a Server folder if none is present in order
to hold all of the files it is passed. Once a file is opened the current thread is locked
to avoid conflicting inputs. The thread is then released once
the file is closed. Multiple threads are supported.
#Client Thread
Client Thread connets to the server then terminates once the entire 
file has been sent the client will terminate. The client displays the
available files for the user to choose from and send to the server.
The user also has the ability to choose a proxy