class MyButton:
    device: str

    def __init__(self, device):
        """
        Sets up path the device file
        :param device: path the device file
        """

        self.device = device

    def is_pressed(self):
        """
        Returns button status
        :return: True if button is pressed | False if not
        """
        with open(self.device, "r") as file:
            status = file.read().strip()
            return status == "1"

