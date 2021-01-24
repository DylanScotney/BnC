
class Address():
    """
    Container for address infomation
    """
    def __init__(self, name="", street="", address1="", address2="", 
                company="", city="", zip="", province="", country="", 
                phone=""):
        self.name = name
        self.street = street
        self.address1 = address1
        self.address2 = address2
        self.company = company
        self.city = city
        self.zip = zip
        self.province = province
        self.country = country
        self.phone = phone

    def __repr__(self):
        return "Address()"

    def __str__(self):

        return_str = ""

        if self.name:
            return_str += self.name + ",<br>"

        if self.company:
            return_str += self.company + ",<br>"

        if self.address1:
            return_str += self.address1 + ",<br>"

        if self.address2:
            return_str += self.address2 + ",<br>"

        if self.city:
            return_str += self.city + ",<br>"

        if self.zip:
            return_str += self.zip.upper() + ",<br>"

        if self.country:
            return_str += self.country + ",<br>"

        if self.phone:
            return_str += self.phone + ",<br>"

        return return_str[:-5]
        
        # return (
        #     "Name: {name}\n"
        #     + "Street: {street}\n"
        #     + "Address1: {address1}\n"
        #     + "Address2: {address2}\n"
        #     + "Company: {company}\n"
        #     + "City: {city}\n"
        #     + "Zip: {zip}\n"
        #     + "Province: {province}\n"
        #     + "Country: {country}\n"
        #     + "Phone: {phone}"
        # ).format(
        #     name=self.name,
        #     street = self.street,
        #     address1 = self.address1,
        #     address2 = self.address2,
        #     company = self.company,
        #     city = self.city,
        #     zip = self.zip,
        #     province = self.province,
        #     country = self.country,
        #     phone = self.phone,
        # )