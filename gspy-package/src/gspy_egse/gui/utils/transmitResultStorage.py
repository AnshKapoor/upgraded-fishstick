class TransmitResultStorage:
    def __init__(self):
        self.result = None

    def set_result(self, transmit_result, data_throughput, total_duration, receivedPackage):
        self.result = (transmit_result, data_throughput, total_duration, receivedPackage)

    def get_result(self):
        return self.result if self.result else ("No result", 0, 0)  # Default values or indication if result not set
