import os
import sys
import paramiko
import time
import re
import getpass

from paramiko import SSHClient

try:
    ssh_client: SSHClient = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
except Exception as e1:
    print("main exception " + str(e1))

if len(sys.argv) < 1:
    print("")
    print("Missing host or config file")
    print("")
    print("Usage take_backup <host_file>")
    print("")

host_file = open(sys.argv[1], 'r')
host_file_read = host_file.readline()
host_format = host_file_read.split(',')

username = input("Enter username : ")
password = getpass.getpass("Enter password: ")
enable_password = getpass.getpass("Enter enable password: ")
wcr_no = input("Enter WCR no: ")

for lines in host_file_read:
    # print(host_format)
    i = 1
    end = len(host_format)
    if end == 1:
        break
    h_list = [word.strip() for word in host_format]
    # print("Length of entry =", end)
    # print("Host and Context List", h_list)
    # print("List length", len(h_list))
    # print("Device name : ", h_list[0])
    try:
        ssh_client.connect(hostname=h_list[0], username=username, password=password,
                           allow_agent=False, look_for_keys=False, timeout=10)
        chan = ssh_client.invoke_shell()
        time.sleep(1)
        if chan.send_ready():
            # pass
            print("Logged in to host %s" % h_list[0])
        else:
            print("Channel not ready")
            sys.exit(1)

        content = ""
        error = ""
        chan.send("enable\n")
        time.sleep(2)
        temp = chan.recv(1024).decode('ascii')
        print(temp)
        if re.search("Password:", temp):
            print("***")
            chan.send("%s\n" % enable_password)
        else:
            print("failed to enable")
            sys.exit(1)

        chan.send("terminal page 0\n")
        chan.send("changeto system\n")
        time.sleep(1)
        temp = chan.recv(5000).decode('ascii')
        print(temp)
        data = ""
        file = open("%s/%s.txt" % (os.getcwd(), wcr_no), 'a+')
        for index in range(i, end):
            context = h_list[index]
            # add call to push config to the context
            time.sleep(1)
            chan.send("changeto context %s\n" % context)
            time.sleep(2)
            temp = chan.recv(1024).decode('ascii')
            print(temp)
            chan.send("show running-config\n")
            chan.send("$\n")
            content = ""
            data = chan.recv(1024).decode('ascii')
            while data:
                content += data
                data = chan.recv(5000).decode('ascii')
                if re.search("ERROR:", data):
                    break
            print("context %s" % context)
            print("Data stored in buffer for %s: \n" % context)
            file.write(content)

        # print(context)
        host_file_read = host_file.readline()
        host_format = host_file_read.split(',')
        ssh_client.close()

    except paramiko.ssh_exception.AuthenticationException:
        print("Authentication Failure")
    except Exception as e:
        print("exception" + str(e))

host_file.close()


























