import os
import posixpath

import ButterAndCrust.images

IMG_DIR = os.path.dirname(ButterAndCrust.images.__file__)

class _BaseItem(object):
    """
    Base lineitem class

    Attributes:
        description(``str``): description of item
        price(``float``, optional): price of item
        img(``str``, optional): file path to image of item 
    """

    def __init__(self, desc, price=None, img=None):
        """
        Instantiates a new instance of the _BaseItem object.

        Args:
            desc(``str``): description of item
            price(``float``, optional): price of item
            img(``str``, optional): file path to image of item
        """
        self._description = desc
        self._price = price
        self._img = img

    def __eq__(self, other):
        """
        Overrides default implementation
        """
        if isinstance(other, self.__class__):
            return self.description == other.description
        return False

    def __str__(self):
        """
        Overrides the default implementation
        """
        return self.description

    @property
    def description(self):
        return self._description

    @property
    def friendly_desc(self):
        return self._description

    @property
    def price(self):
        return self._price

    @property
    def img(self):
        return self._img

class _BaseFriendlyItem(_BaseItem):
    """
    Base lineitem class that has a seperate customer friendly 
    description

    Attributes:
        friendly_desc(``str``): Customer friendly description
    """

    def __init__(self, desc, friendly_desc, price=None, img=None):
        """
        Instantiates a new instance of a _BaseFriendlyItem 
        class.

        Args:
            desc(``str``): description of item
            friendly_desc(``str``): customer friendly description
            price(``float``, optional): price of item
            img(``str``, optional): file path to image of item

        """
        super().__init__(desc, price, img)
        self._friendly_desc = friendly_desc

    @property
    def friendly_desc(self):
        """
        Overrides default implementation
        """
        return self._friendly_desc

class _DefaultCoffeeItem(_BaseFriendlyItem):
    """
    Default coffee item used if item is unmatched
    """

    IMG = posixpath.join(IMG_DIR, "Coffee_logo.png")

    def __init__(self, desc, price=None):
        friendly_desc = desc.split("250g", 1)[0] + "250g"
        super().__init__(desc, friendly_desc, price=price, img=self.IMG)

class Lineitems(object):
    """
    To Do:

    Add images and prices to classes
    """

    class Subscription(_BaseItem):
        """
        The standard butter and crust subscription
        """
        
        DESCRIPTION = "Butter & Crust Subscription (Loaf Included)"
        IMG = posixpath.join(IMG_DIR, "Subscription_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, img=self.IMG)

    class ExtraLoaf(_BaseItem):
        """
        An addition loaf of sourdough
        """

        DESCRIPTION = "Extra Loaf"
        IMG = posixpath.join(IMG_DIR, "ExtraLoaf_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, img=self.IMG)

    class SweetMorningTreats(_BaseItem):
        """
        Pastries and cakes
        """

        DESCRIPTION = "Sweet Morning Treats"
        IMG = posixpath.join(IMG_DIR, "Pastries_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, img=self.IMG)
    
    class AppleJuice(_BaseItem):
        """
        Bottle of apple juice
        """

        DESCRIPTION = "Townsend Farm Apple Juice 750ml"
        IMG = posixpath.join(IMG_DIR, "AppleJuice_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, img=self.IMG)

    class Granola(_BaseItem):
        """
        Granola
        """

        DESCRIPTION = "Granola"
        IMG = posixpath.join(IMG_DIR, "Granola_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, img=self.IMG)

    class CulteredButter(_BaseItem):
        """
        Cultered butter
        """

        DESCRIPTION = "Cultured Butter 250g"
        IMG = posixpath.join(IMG_DIR, "CulturedButter_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, img=self.IMG)

    class Preserves(_BaseItem):
        """
        Preserves
        """

        DESCRIPTION = "Preserves 125g"
        IMG = posixpath.join(IMG_DIR, "Preserves_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, img=self.IMG)

    class ClassicWeeklyWholebean(_BaseFriendlyItem):
        """
        Classic wholebean coffee delivered weekly
        """

        DESCRIPTION = "Monmouth Coffee. - Classic / Wholebean / 250g per week"
        FRIENDLY_DESC = "Monmouth Coffee. - Classic / Wholebean / 250g"
        IMG = posixpath.join(IMG_DIR, "ClassicCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class ClassicBiWeeklyWholebean(_BaseFriendlyItem):
        """
        Classic wholebean coffee delivered every other week
        """

        DESCRIPTION = "Monmouth Coffee. - Classic / Wholebean / 250g every other week"
        FRIENDLY_DESC = "Monmouth Coffee. - Classic / Wholebean / 250g"
        IMG = posixpath.join(IMG_DIR, "ClassicCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class EspressoWeeklyWholebean(_BaseFriendlyItem):
        """
        Espresso wholebean coffee delivered weekly
        """

        DESCRIPTION = "Monmouth Coffee. - Espresso / Wholebean / 250g per week"
        FRIENDLY_DESC = "Monmouth Coffee. - Espresso / Wholebean / 250g"
        IMG = posixpath.join(IMG_DIR, "EspressoCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)
    
    class EspressoBiWeeklyWholebean(_BaseFriendlyItem):
        """
        Espresso wholebean coffee delivered weekly
        """

        DESCRIPTION = "Monmouth Coffee. - Espresso / Wholebean / 250g every other week"
        FRIENDLY_DESC = "Monmouth Coffee. - Espresso / Wholebean / 250g"
        IMG = posixpath.join(IMG_DIR, "EspressoCoffee_logo.png")
            
        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class OurPickWeeklyWholebean(_BaseFriendlyItem):
        """
        Our pick of wholebean coffee delivered weekly
        """

        DESCRIPTION = "Monmouth Coffee. - Our Pick / Wholebean / 250g per week"
        FRIENDLY_DESC = "Monmouth Coffee. - Our Pick / Wholebean / 250g"
        IMG = posixpath.join(IMG_DIR, "OurPickCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class OurPickBiWeeklyWholebean(_BaseFriendlyItem):
        """
        Our pick of wholebean coffee delivered every other week
        """
        
        DESCRIPTION = "Monmouth Coffee. - Our Pick / Wholebean / 250g every other week"
        FRIENDLY_DESC = "Monmouth Coffee. - Our Pick / Wholebean / 250g"
        IMG = posixpath.join(IMG_DIR, "OurPickCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class ClassicWeeklyCoarse(_BaseFriendlyItem):
        """
        Classic Coarse coffee delivered weekly
        """
        
        DESCRIPTION = "Monmouth Coffee. - Classic / Coarse / 250g per week"
        FRIENDLY_DESC = "Monmouth Coffee. - Classic / Coarse / 250g"
        IMG = posixpath.join(IMG_DIR, "ClassicCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class ClassicBiWeeklyCoarse(_BaseFriendlyItem):
        """
        Classic Coarse coffee delivered every other week
        """
        
        DESCRIPTION = "Monmouth Coffee. - Classic / Coarse / 250g every other week"
        FRIENDLY_DESC = "Monmouth Coffee. - Classic / Coarse / 250g"
        IMG = posixpath.join(IMG_DIR, "ClassicCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class EspressoWeeklyCoarse(_BaseFriendlyItem):
        """
        Espresso Coarse coffee delivered weekly
        """
        
        DESCRIPTION = "Monmouth Coffee. - Espresso / Coarse / 250g per week"
        FRIENDLY_DESC = "Monmouth Coffee. - Espresso / Coarse / 250g"
        IMG = posixpath.join(IMG_DIR, "EspressoCoffee_logo.png")
            
        def __init__(self):super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)
    
    class EspressoBiWeeklyCoarse(_BaseFriendlyItem):
        """
        Espresso Coarse coffee delivered weekly
        """
        
        DESCRIPTION = "Monmouth Coffee. - Espresso / Coarse / 250g every other week"
        FRIENDLY_DESC = "Monmouth Coffee. - Espresso / Coarse / 250g"
        IMG = posixpath.join(IMG_DIR, "EspressoCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class OurPickWeeklyCoarse(_BaseFriendlyItem):
        """
        Our pick of Coarse coffee delivered weekly
        """
        
        DESCRIPTION = "Monmouth Coffee. - Our Pick / Coarse / 250g per week"
        FRIENDLY_DESC = "Monmouth Coffee. - Our Pick / Coarse / 250g"
        IMG = posixpath.join(IMG_DIR, "OurPickCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class OurPickBiWeeklyCoarse(_BaseFriendlyItem):
        """
        Our pick of Coarse coffee delivered every other week
        """
        
        DESCRIPTION = "Monmouth Coffee. - Our Pick / Coarse / 250g every other week"
        FRIENDLY_DESC = "Monmouth Coffee. - Our Pick / Coarse / 250g"
        IMG = posixpath.join(IMG_DIR, "OurPickCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class ClassicWeeklyMedium(_BaseFriendlyItem):
        """
        Classic Medium coffee delivered weekly
        """
        
        DESCRIPTION = "Monmouth Coffee. - Classic / Medium / 250g per week"
        FRIENDLY_DESC = "Monmouth Coffee. - Classic / Medium / 250g"
        IMG = posixpath.join(IMG_DIR, "ClassicCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class ClassicBiWeeklyMedium(_BaseFriendlyItem):
        """
        Classic Medium coffee delivered every other week
        """
        
        DESCRIPTION = "Monmouth Coffee. - Classic / Medium / 250g every other week"
        FRIENDLY_DESC = "Monmouth Coffee. - Classic / Medium / 250g"
        IMG = posixpath.join(IMG_DIR, "ClassicCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class EspressoWeeklyMedium(_BaseFriendlyItem):
        """
        Espresso Medium coffee delivered weekly
        """
        
        DESCRIPTION = "Monmouth Coffee. - Espresso / Medium / 250g per week"
        FRIENDLY_DESC = "Monmouth Coffee. - Espresso / Medium / 250g"
        IMG = posixpath.join(IMG_DIR, "EspressoCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)
    
    class EspressoBiWeeklyMedium(_BaseFriendlyItem):
        """
        Espresso Medium coffee delivered weekly
        """
        
        DESCRIPTION = "Monmouth Coffee. - Espresso / Medium / 250g every other week"
        FRIENDLY_DESC = "Monmouth Coffee. - Espresso / Medium / 250g"
        IMG = posixpath.join(IMG_DIR, "EspressoCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class OurPickWeeklyMedium(_BaseFriendlyItem):
        """
        Our pick of Medium coffee delivered weekly
        """
        
        DESCRIPTION = "Monmouth Coffee. - Our Pick / Medium / 250g per week"
        FRIENDLY_DESC = "Monmouth Coffee. - Our Pick / Medium / 250g"
        IMG = posixpath.join(IMG_DIR, "OurPickCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class OurPickBiWeeklyMedium(_BaseFriendlyItem):
        """
        Our pick of Medium coffee delivered every other week
        """
        
        DESCRIPTION = "Monmouth Coffee. - Our Pick / Medium / 250g every other week"
        FRIENDLY_DESC = "Monmouth Coffee. - Our Pick / Medium / 250g"
        IMG = posixpath.join(IMG_DIR, "OurPickCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    
    class ClassicWeeklyFine(_BaseFriendlyItem):
        """
        Classic Fine coffee delivered weekly
        """
        
        DESCRIPTION = "Monmouth Coffee. - Classic / Fine / 250g per week"
        FRIENDLY_DESC = "Monmouth Coffee. - Classic / Fine / 250g"
        IMG = posixpath.join(IMG_DIR, "ClassicCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class ClassicBiWeeklyFine(_BaseFriendlyItem):
        """
        Classic Fine coffee delivered every other week
        """
        
        DESCRIPTION = "Monmouth Coffee. - Classic / Fine / 250g every other week"
        FRIENDLY_DESC = "Monmouth Coffee. - Classic / Fine / 250g"
        IMG = posixpath.join(IMG_DIR, "ClassicCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class EspressoWeeklyFine(_BaseFriendlyItem):
        """
        Espresso Fine coffee delivered weekly
        """
        
        DESCRIPTION = "Monmouth Coffee. - Espresso / Fine / 250g per week"
        FRIENDLY_DESC = "Monmouth Coffee. - Espresso / Fine / 250g"
        IMG = posixpath.join(IMG_DIR, "EspressoCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)
    
    class EspressoBiWeeklyFine(_BaseFriendlyItem):
        """
        Espresso Fine coffee delivered weekly
        """
        
        DESCRIPTION = "Monmouth Coffee. - Espresso / Fine / 250g every other week"
        FRIENDLY_DESC = "Monmouth Coffee. - Espresso / Fine / 250g"
        IMG = posixpath.join(IMG_DIR, "EspressoCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class OurPickWeeklyFine(_BaseFriendlyItem):
        """
        Our pick of Fine coffee delivered weekly
        """
        
        DESCRIPTION = "Monmouth Coffee. - Our Pick / Fine / 250g per week"
        FRIENDLY_DESC = "Monmouth Coffee. - Our Pick / Fine / 250g"
        IMG = posixpath.join(IMG_DIR, "OurPickCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    class OurPickBiWeeklyFine(_BaseFriendlyItem):
        """
        Our pick of Fine coffee delivered every other week
        """
        
        DESCRIPTION = "Monmouth Coffee. - Our Pick / Fine / 250g every other week"
        FRIENDLY_DESC = "Monmouth Coffee. - Our Pick / Fine / 250g"
        IMG = posixpath.join(IMG_DIR, "OurPickCoffee_logo.png")

        def __init__(self):
            super().__init__(self.DESCRIPTION, self.FRIENDLY_DESC, img=self.IMG)

    @classmethod
    def _discover_items(cls):
        """
        Discovers matched lineitem classes. 

        Returns:
            cls.items(``dict``): dict of lineitems where lineitem
                description is key and class is value
        """

        try:
            return cls.items
        except AttributeError:
            items = {}
            for item_name in dir(cls):
                item_class = getattr(cls, item_name)
                if hasattr(item_class, "DESCRIPTION"):
                    items[item_class.DESCRIPTION] = item_class()
            cls.items = items
        return cls.items

    @classmethod
    def get(cls, description):
        """
        Returns a Lineitem class instance, by its description.

        If the description is unmatched, will create a generic
        item instance.
        """

        item_classes = cls._discover_items()
        try:
            item = item_classes[description]
        except KeyError:
            # if unmatched
            if "coffee" in description.lower():
                item = _DefaultCoffeeItem(description)
            else:
                item = _BaseItem(description)
        
        return item
