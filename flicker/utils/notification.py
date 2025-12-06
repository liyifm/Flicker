class NotificationManager:
    @staticmethod
    def send_info_message(title: str, message: str):
        from flicker.gui.application import FlickerApp
        FlickerApp.sendInfoMessage(title, message)

    @staticmethod
    def send_error_message(title: str, message: str):
        from flicker.gui.application import FlickerApp
        FlickerApp.sendErrorMessage(title, message)
