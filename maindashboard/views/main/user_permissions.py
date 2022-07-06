class Permissions:
    def __init__(self):
        self.WAREHOUSE_DELIVERYPARTY = 'warehouse_deliveryParty'
        self.WAREHOUSE_MARKING = 'warehouse_marking'
        self.WAREHOUSE_ITEMS = 'warehouse_items'
        self.WAREHOUSE_VERIFY = 'warehouse_verify'

        self.STUFFING_CONTAINER = 'stuffing_container'

        self.permission_list = [
            self.WAREHOUSE_DELIVERYPARTY,
            self.WAREHOUSE_MARKING,
            self.WAREHOUSE_ITEMS,
            self.WAREHOUSE_VERIFY,
            self.STUFFING_CONTAINER,
        ]


permissions = Permissions()
