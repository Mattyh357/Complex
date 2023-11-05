import sys
import time


class App:
    def __init__(self):
        self.who = "World"

    def run(self):
        self.main_loop()

    def main_loop(self):
        while True:
            print("Hello " + self.who + "!")
            time.sleep(1)



if __name__ == '__main__':
    app = App()
    app.run()
