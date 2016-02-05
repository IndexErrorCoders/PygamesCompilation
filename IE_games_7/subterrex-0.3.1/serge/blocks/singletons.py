"""Implement a store for singletons"""

import serge.serialize
import serge.registry



class SingletonStore(serge.registry.GeneralStore):
    """A store for global objects"""

    def _registerItem(self, name):
        """Register a new item"""
        item = serge.serialize.Bag()
        self.items[name] = item
        return item



Store = SingletonStore()


