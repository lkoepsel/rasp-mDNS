from zeroconf import ZeroconfServiceTypes
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf


class MyListener(ServiceListener):

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} updated")

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} removed")

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        print(f"Service {name} added, service info: {info}")


zeroconf = Zeroconf()
listener = MyListener()
services = ZeroconfServiceTypes.find()
# print('\n'.join(ZeroconfServiceTypes.find()))

for service in services:
    print(f"\n****{service}****\n")
    browser = ServiceBrowser(zeroconf, service, listener)
    print(f"{browser=}")

try:
    input("Press enter to exit...\n\n")
finally:
    zeroconf.close()
