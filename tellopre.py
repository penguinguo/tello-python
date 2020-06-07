#一部分引入
from threading import Thread
import time
import socket
import select
import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as tkm

#参数

UDP_IP_Tello="192.168.10.1"
UDP_PORT_Command = 8889
UDP_PORT_Command_Local=8880

UDP_IP_Local = "0.0.0.0"
UDP_PORT_State = 8890
UDP_PORT_Stream = 11111
#  定义sender

class Sender(Thread):
    MESSAGE = b"Hello, world"
    def __init__(self, sock):
        # Call Thread constructor
        super().__init__()
        self.sock = sock
        self.keep_running = True

    def stop(self):
        # Call this from another thread to stop the sender
        self.keep_running = False

    def run(self):
        # This will run when you call .start method
        while self.keep_running:
            print("Sending Message.")
            try:
                self.sock.sendto(self.MESSAGE, (UDP_IP, UDP_PORT))
                time.sleep(0.5) # REMOVE ME: Just to slow things down a bit for debugging
            except socket.error as err:
                print("Error from sending socket {}".format(err))
                break

 #定义  receiver
class Receiver(Thread):
    def __init__(self, sock):
        # Call Thread constructor
        super().__init__()
        self.sock = sock
        self.keep_running = True

    def stop(self):
        # Call this from another thread to stop the receiver
        self.keep_running = False

    def run(self):
        # This will run when you call .start method
        while self.keep_running:
            # We use select here so that we are not *hung* forever in recvfrom.
            # We'll wake up every0.5 seconds to check whether we should keep running
            rfds, _wfds, _xfds = select.select([self.sock], [], [], 0.01)
            if self.sock in rfds:
                try:
                    data, addr = self.sock.recvfrom(1024)
                    print("received message:", data)
                    print("from: ", addr)
                except socket.error as err:
                    print("Error from receiving socket {}".format(err))
                    break

# 定义    App
class App(tk.Frame):
    STRIDE = 8
    DELAY = 100

    # pythonic list comprehensions equivalent to your previous loops
    variables = [i for i in range(10)]
    sensors = [i for i in range(3)]
    fields = [i for i in range(len(sensors) * len(variables))]

    def __init__(self, sock_cmd,sock_state,sock_stream, master=None):
        # Call superclass constructor
        super().__init__(master)
        self.sock_cmd = sock_cmd
        self.sock_state = sock_state
        self.sock_stream = sock_stream
        self.sender = None
        self.receiver = None
        self.grid()
        self.create_widgets()
        self.update()

    #---- Create the GUI Layout ----
    def create_widgets(self):
        self.btn_font = tkFont.Font(family="Helvetica", size=12, weight='bold')
        self.gui_buttons = []
        # Buttons renamed for orthogonality
        self.sstart_button = tk.Button(self,
                                     text = format("Begin Sending."),
                                     font = self.btn_font,
                                     relief = tk.RIDGE,
                                     pady = 4,
                                     command = self.start_sending)
        self.sstart_button.grid(column=2, row=11)

        # Adding a stop button for the sender too
        self.sstop_button = tk.Button(self,
                                     text = format("Stop Sending."),
                                     font = self.btn_font,
                                     relief = tk.RIDGE,
                                     pady = 4,
                                     padx = 6,
                                     state='disabled',
                                     command = self.stop_sending)

        self.sstop_button.grid(column=2, row=12)

        self.rstart_button = tk.Button(self,
                                 text = format("Begin Receiving."),
                                 font = self.btn_font,
                                 relief = tk.RIDGE,
                                 pady = 4,
                                 command = self.start_receiving)
        self.rstart_button.grid(column=3, row=11)
        self.rstop_button = tk.Button(self,
                                     text = format("Stop Receiving."),
                                     font = self.btn_font,
                                     relief = tk.RIDGE,
                                     pady = 4,
                                     padx = 6,
                                     state='disabled',
                                     command = self.stop_receiving)

        self.rstop_button.grid(column=3, row=12)
        x = 0
        y = 1
        for i, label in enumerate(self.variables):
            label = tk.Label(self,
                                text = format("Variable " + str(i)),
                                font = self.btn_font,
                                padx = 10)
            label.grid(column=x, row=y)
            y += 1

        x = 1
        y = 0
        for i, label in enumerate(self.sensors):
            sensor = tk.Label(self,
                                text = format("Sensor " + str(i)),
                                font = self.btn_font,
                                padx = 20,
                                relief = tk.RIDGE)
            sensor.grid(column=x, row=y)
            x += 1

        x = 1
        y = 1
        for i, field in enumerate(self.fields):
            field = tk.Entry(self,
                             width=10,
                             text=format("field val " + str(i)),
                             font=self.btn_font,
                             state='disabled')
            field.grid(column=x, row=y)
            y += 1
            if y > len(self.variables):
                y = 1
                x += 1

    def mainloop(self, *args):
        # Overriding mainloop so that we can do cleanup of our threads
        # *If* any arguments were provided, we would pass them on to Tk.frame
        super().mainloop(*args)

        # When main loop finishes, shutdown sender and/or receiver if necessary
        if self.sender:
            self.sender.stop()
        if self.receiver:
            self.receiver.stop()


    #----Start the receiver thread
    def start_receiving(self):
        self.rstart_button.config(state='disabled')
        self.rstop_button.config(state='normal')
        # Create and start receiver thread
        self.receiver = Receiver(self.sock)
        self.receiver.start()

    #----Stop the receiver
    def stop_receiving(self):
        self.rstop_button.config(state='disabled')
        self.rstart_button.config(state='normal')
        self.receiver.stop()
        self.receiver.join()
        self.receiver = None

    #----Start the sender thread
    def start_sending(self):
        self.sstart_button.config(state='disabled')
        self.sstop_button.config(state='normal')
        self.sender = Sender(self.sock)
        self.sender.start()

    #----Stop the sender
    def stop_sending(self):
        self.sstop_button.config(state='disabled')
        self.sstart_button.config(state='normal')
        self.sender.stop()
        self.sender.join()
        self.sender = None
#定义     main
def main():
    # Got rid of sock as global variable
    sock_cmd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_cmd.bind((UDP_IP_Local, UDP_PORT_Command_Local))
    
    sock_state = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_state.bind((UDP_IP_Local, UDP_PORT_State))
    
    sock_stream = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_stream.bind((UDP_IP_Local, UDP_PORT_Stream))


    app = App(sock_cmd,sock_state,sock_stream)
    app.master.title('Tello 控制中心-Powered by Penguin')
    app.master.geometry('1000x700')
    app.mainloop()
#结尾
if __name__ == '__main__':
    main()

