class Permissions:
    def __init__(self):
        self.WAREHOUSE_DELIVERYPARTY = 'warehouse.delivery_party'
        self.WAREHOUSE_MARKING = 'warehouse.marking'
        self.WAREHOUSE_ITEMS = 'warehouse.items'
        self.WAREHOUSE_VERIFY = 'warehouse.verify'

        self.STUFFING_CONTAINER = 'stuffing.container'

        self.permission_list = [
            self.WAREHOUSE_DELIVERYPARTY,
            self.WAREHOUSE_MARKING,
            self.WAREHOUSE_ITEMS,
            self.WAREHOUSE_VERIFY,
            self.STUFFING_CONTAINER,
        ]


permissions = Permissions()
